"""Exercise archive preservation, event filtering, version capture and opt-in scope."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'skills/save-trace/scripts/save_trace.py'
spec = importlib.util.spec_from_file_location('save_trace', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SID = 'sample-session-001'


def event(kind, payload):
    return {'timestamp': '2026-10-09T15:00:00Z', 'type': kind, 'payload': payload}


def message(role, text, **kwargs):
    return event('response_item', {'type': 'message', 'role': role, 'content': [{'type': 'output_text', 'text': text}], **kwargs})


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.skill = self.repo / 'skills/teach-me/SKILL.md'
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text('original skill\n')
        (self.repo / 'AGENTS.md').write_text('workspace rules\n')
        (self.repo / 'CONTEXT.md').write_text('definitions\n')
        self.role = self.repo / 'tests/roles/example'
        self.role.mkdir(parents=True)
        (self.repo / 'docs').mkdir()
        self.feedback = self.repo / 'docs/feedback.md'
        self.feedback.write_text('Human feedback is maintained separately.\n')
        self.source = self.root / 'rollout.jsonl'
        self.records = [
            event('session_meta', {'id': SID, 'timestamp': '2026-10-09T15:00:00Z', 'originator': 'Codex Desktop', 'cli_version': 'test-version', 'model_provider': 'openai', 'base_instructions': 'INTERNAL_SYSTEM'}),
            event('turn_context', {'turn_id': 't1', 'model': 'model-a', 'effort': 'high', 'summary': 'INTERNAL_SUMMARY'}),
            message('user', 'Please give a concrete example.'),
            message('assistant', 'Here is an example.'),
            event('response_item', {'type': 'custom_tool_call', 'call_id': 'c1', 'name': 'read_file', 'input': 'example.py'}),
            event('response_item', {'type': 'custom_tool_call_output', 'call_id': 'c1', 'output': 'file content'}),
            event('turn_context', {'turn_id': 't2', 'model': 'model-b', 'effort': 'low'}),
            message('user', 'This explanation helped.'),
            message('system', 'INTERNAL_SYSTEM_MESSAGE'),
            message('assistant', 'INTERNAL_ANALYSIS', channel='analysis'),
            event('response_item', {'type': 'reasoning', 'summary': 'INTERNAL_REASONING', 'encrypted_content': 'INTERNAL_CIPHER'}),
            event('compacted', {'message': 'INTERNAL_COMPACTION', 'replacement_history': []}),
        ]
        self.write_source()

    def write_source(self):
        self.source.write_text(''.join(json.dumps(r) + '\n' for r in self.records))

    def save(self, **kwargs):
        return module.archive(self.source, self.repo, self.role, 'Learn a mechanism', session_id=SID, **kwargs)

    def test_exports_actual_events_and_model_timeline_without_feedback_mutation(self):
        out, meta = self.save(skills_used=['teach-me'])
        self.assertEqual(['model-a', 'model-b'], [t['model'] for t in meta['models_by_turn']])
        self.assertEqual('test-version', meta['harness']['cli_version'])
        trace = (out / 'trace.jsonl').read_text()
        self.assertNotIn('INTERNAL_', trace)
        self.assertIn('This explanation helped.', trace)
        events = [json.loads(line) for line in trace.splitlines()]
        self.assertEqual(['tool_call', 'tool_result'], [e['type'] for e in events if e['type'].startswith('tool_')])
        self.assertIn('## e0000008', (out / 'conversation.md').read_text())
        self.assertEqual('Human feedback is maintained separately.\n', self.feedback.read_text())
        self.assertFalse((self.role / 'learning-state').exists())
        self.assertFalse((self.role / 'trials').exists())
        self.assertIsNone(meta['saves'][0]['git_commit_at_save'])

    def test_repeated_save_is_idempotent_and_new_messages_extend_same_run(self):
        out, first = self.save()
        before = (out / 'trace.jsonl').read_bytes()
        again, second = self.save()
        self.assertEqual(out, again)
        self.assertEqual(1, len(second['saves']))
        self.assertEqual(before, (out / 'trace.jsonl').read_bytes())
        self.records.append(message('user', 'Next question.'))
        self.write_source()
        _, third = self.save()
        self.assertEqual(2, len(third['saves']))
        self.assertTrue((out / 'trace.jsonl').read_bytes().startswith(before))
        self.assertEqual(1, len(list((self.role / 'runs').iterdir())))

    def test_git_commit_and_untracked_skills_are_both_preserved(self):
        def git(*args):
            return subprocess.run(['git', '-C', str(self.repo), *args], check=True, capture_output=True, text=True).stdout.strip()
        git('init', '-q')
        git('add', 'AGENTS.md', 'CONTEXT.md', 'skills')
        git('-c', 'user.name=Trace Test', '-c', 'user.email=trace@example.invalid', 'commit', '-qm', 'baseline')
        head = git('rev-parse', 'HEAD')
        self.skill.write_text('changed after commit\n')
        extra = self.repo / 'skills/teach-me/extra.md'
        extra.write_text('untracked dependency\n')
        out, first = self.save()
        self.assertEqual(head, first['saves'][0]['git_commit_at_save'])
        self.assertTrue(first['saves'][0]['skill_files_dirty_at_save'])
        old_bundle = first['skill_versions'][0]['bundle']
        snapshot = out / 'skill-snapshot' / old_bundle
        self.assertEqual('untracked dependency\n', (snapshot / 'skills/teach-me/extra.md').read_text())
        self.skill.write_text('another change\n')
        _, second = self.save()
        self.assertEqual(2, len(second['skill_versions']))
        self.assertEqual('changed after commit\n', (snapshot / 'skills/teach-me/SKILL.md').read_text())
        self.assertEqual(2, len(second['saves']))

    def test_incomplete_tail_is_deferred_until_complete(self):
        with self.source.open('ab') as f:
            f.write(b'{"type":')
        out, first = self.save()
        self.assertGreater(first['saves'][0]['pending_tail_bytes'], 0)
        self.records.append(message('assistant', 'Completed later.'))
        self.write_source()
        _, second = self.save()
        self.assertEqual(0, second['saves'][-1]['pending_tail_bytes'])
        self.assertIn('Completed later.', (out / 'conversation.md').read_text())

    def test_truncated_or_rewritten_source_cannot_destroy_archive(self):
        out, _ = self.save()
        before = (out / 'trace.jsonl').read_bytes()
        self.records = self.records[:-2]
        self.write_source()
        with self.assertRaisesRegex(ValueError, '截断'):
            self.save()
        self.assertEqual(before, (out / 'trace.jsonl').read_bytes())

    def test_wrong_session_or_bad_log_creates_no_run(self):
        with self.assertRaisesRegex(ValueError, '不一致'):
            module.archive(self.source, self.repo, self.role, 'task', session_id='another-session')
        with self.source.open('a') as f:
            f.write('not-json\n')
        with self.assertRaisesRegex(ValueError, '不是有效 JSON'):
            self.save()
        self.assertFalse((self.role / 'runs').exists())

    def test_missing_model_is_unknown_and_unknown_events_are_counted(self):
        self.records = [self.records[0], message('user', 'Hello'), event('future_event', {'x': 1})]
        self.write_source()
        out, meta = self.save()
        self.assertEqual([], meta['models_by_turn'])
        self.assertEqual(1, meta['omitted_record_counts']['future_event'])
        self.assertIn('模型：未知', (out / 'run.md').read_text())

    def test_cli_executes_without_api_or_third_party_packages(self):
        result = subprocess.run(['python3', str(SCRIPT), '--source', str(self.source), '--repo', str(self.repo), '--role-dir', str(self.role), '--session-id', SID, '--task', 'CLI test'], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(SID, json.loads(result.stdout)['session_id'])


if __name__ == '__main__':
    unittest.main()
