#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archive one explicitly selected Codex rollout. Uses only the Python stdlib."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from zoneinfo import ZoneInfo


SCHEMA = 1


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pick(value, names):
    return {key: value[key] for key in names if key in value}


def text_parts(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ''
    parts = []
    for part in content:
        if isinstance(part, dict) and part.get('type') in {'text', 'input_text', 'output_text'}:
            parts.append(part.get('text', ''))
        else:
            parts.append('[非文本内容；本次归档未复制媒体]')
    return '\n'.join(parts)


def parse_rollout(source):
    raw = source.read_bytes()
    records, offset = [], 0
    for number, line in enumerate(raw.splitlines(keepends=True), 1):
        try:
            record = json.loads(line)
        except (ValueError, UnicodeError):
            if offset + len(line) == len(raw) and not line.endswith(b'\n'):
                break  # An actively written final record will be read on the next save.
            raise ValueError(f'日志第 {number} 行不是有效 JSON；未更新归档')
        if not isinstance(record, dict) or not isinstance(record.get('payload'), dict):
            raise ValueError(f'日志第 {number} 行结构不受支持')
        records.append((number, record))
        offset += len(line)
    metas = [r['payload'] for _, r in records if r.get('type') == 'session_meta']
    if not metas or not metas[0].get('id'):
        raise ValueError('日志缺少 session_meta.id，无法确定测试会话')
    if any(m.get('id') != metas[0]['id'] for m in metas):
        raise ValueError('日志混入多个会话 ID')
    return raw[:offset], records, metas[0], len(raw) - offset


def export_events(records):
    events, skipped, turns = [], Counter(), []
    turn_id = None
    for line, record in records:
        kind, payload = record.get('type'), record['payload']
        data = None
        if kind == 'session_meta':
            data = pick(payload, ['id', 'timestamp', 'cwd', 'originator', 'cli_version', 'model_provider', 'git'])
        elif kind == 'turn_context':
            turn_id = payload.get('turn_id')
            data = pick(payload, ['turn_id', 'cwd', 'model', 'effort', 'approval_policy', 'sandbox_policy', 'current_date', 'timezone'])
            turns.append({'event_id': f'e{line:07d}', 'timestamp': record.get('timestamp'), **data})
        elif kind == 'response_item':
            item = payload.get('type')
            if item == 'message' and payload.get('role') in {'user', 'assistant'} and payload.get('channel') in {None, 'final', 'commentary'}:
                kind = 'message'
                data = {'role': payload['role'], 'text': text_parts(payload.get('content')), **pick(payload, ['channel'])}
            elif item in {'function_call', 'custom_tool_call'}:
                kind = 'tool_call'
                data = pick(payload, ['type', 'call_id', 'name', 'arguments', 'input', 'status'])
            elif item in {'function_call_output', 'custom_tool_call_output'}:
                kind = 'tool_result'
                data = pick(payload, ['type', 'call_id', 'output', 'status'])
            else:
                skipped[f'response_item:{item}'] += 1
                continue
        elif kind == 'token_usage_record':
            data = pick(payload, ['turn_id', 'usage', 'turn_token_usage', 'thread_token_usage'])
        elif kind == 'compacted':
            data = {'note': '源日志发生上下文压缩；摘要及内部替换上下文未导出'}
        else:
            skipped[str(kind)] += 1
            continue
        events.append({'id': f'e{line:07d}', 'source_line': line, 'timestamp': record.get('timestamp'), 'turn_id': turn_id, 'type': kind, 'data': data})
    return events, turns, dict(skipped)


def git_value(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def skill_files(repo):
    paths = [repo / 'AGENTS.md', repo / 'CONTEXT.md']
    paths += list((repo / 'skills').rglob('*'))
    files = {}
    for path in sorted(paths):
        if path.is_symlink():
            raise ValueError(f'技能快照遇到符号链接，请先确认其内容：{path}')
        if path.is_file() and '__pycache__' not in path.parts and path.name != '.DS_Store':
            files[str(path.relative_to(repo))] = path.read_bytes()
    if not files:
        raise ValueError('未找到 skills/、AGENTS.md 或 CONTEXT.md；请指定技能仓库')
    return files


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        f.write(data)
        temp = Path(f.name)
    temp.replace(path)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def archive(source, repo, role_dir, task, session_id=None, skills_used=(), learning_dir=None):
    source, repo, role_dir = source.resolve(), repo.resolve(), role_dir.resolve()
    if not role_dir.is_dir():
        raise ValueError('岗位目录不存在；请明确选择已有目标岗位')
    prefix, records, meta, pending = parse_rollout(source)
    sid = meta['id']
    if not isinstance(sid, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', sid):
        raise ValueError('会话 ID 格式无效')
    if session_id and sid != session_id:
        raise ValueError('指定会话 ID 与日志不一致')
    start = meta.get('timestamp') or records[0][1].get('timestamp')
    try:
        date = datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone(ZoneInfo('Asia/Shanghai')).date().isoformat()
    except (AttributeError, ValueError, TypeError):
        raise ValueError('日志缺少可解析的会话开始时间')
    output = role_dir / 'runs' / f'{date}-{sid}'
    manifest_path = output / 'run.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    if previous:
        if previous.get('schema_version') != SCHEMA or previous.get('session_id') != sid:
            raise ValueError('已有归档的版本或会话 ID 不匹配')
        last = previous['saves'][-1]
        size = last['source_bytes']
        if len(prefix) < size or digest(prefix[:size]) != last['source_sha256']:
            raise ValueError('源日志被截断或旧内容已变化；保留已有归档，请检查日志来源')
    elif output.exists() and any(output.iterdir()):
        raise ValueError('目标目录已有内容但缺少 run.json；请检查后再归档')
    events, turns, skipped = export_events(records)
    files = skill_files(repo)
    hashes = {name: digest(data) for name, data in files.items()}
    bundle = digest(json.dumps(hashes, sort_keys=True).encode())
    head = git_value(repo, 'rev-parse', 'HEAD')
    status = git_value(repo, 'status', '--porcelain', '--untracked-files=all', '--', 'skills', 'AGENTS.md', 'CONTEXT.md')
    now = datetime.now(timezone.utc).isoformat()
    save = {'archived_at': now, 'cutoff': records[-1][1].get('timestamp'), 'source_bytes': len(prefix), 'source_sha256': digest(prefix), 'source_records': len(records), 'pending_tail_bytes': pending, 'event_count': len(events), 'skill_bundle': bundle, 'git_commit_at_save': head, 'skill_files_dirty_at_save': bool(status) if status is not None else None, 'reported_skills': list(skills_used)}
    manifest = previous or {'schema_version': SCHEMA, 'session_id': sid, 'started_at': start, 'role': role_dir.name, 'tasks': [], 'learning_records': [], 'saves': [], 'skill_versions': []}
    if task not in manifest['tasks']:
        manifest['tasks'].append(task)
    if learning_dir and str(learning_dir.resolve()) not in manifest['learning_records']:
        manifest['learning_records'].append(str(learning_dir.resolve()))
    manifest.update({'source_log': str(source), 'models_by_turn': turns, 'harness': pick(meta, ['originator', 'cli_version', 'model_provider']), 'git_at_session_start_reported_by_log': meta.get('git'), 'omitted_record_counts': skipped})
    # Identical repeated exports do not create duplicate save records.
    signature = ['source_sha256', 'skill_bundle', 'git_commit_at_save', 'reported_skills', 'pending_tail_bytes']
    if not manifest['saves'] or any(save[k] != manifest['saves'][-1].get(k) for k in signature):
        manifest['saves'].append(save)
    if not any(v['bundle'] == bundle for v in manifest['skill_versions']):
        manifest['skill_versions'].append({'bundle': bundle, 'captured_at': now, 'meaning': '归档时文件快照；不推定此前回合使用此版本', 'files': hashes})
    output.mkdir(parents=True, exist_ok=True)
    snapshot = output / 'skill-snapshot' / bundle
    for name, data in files.items():
        dest = snapshot / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest.read_bytes()) != hashes[name]:
            raise ValueError('已有技能快照内容被修改')
        if not dest.exists():
            dest.write_bytes(data)
    trace = ''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in events)
    conversation = ['# 对话内容\n', f'会话：`{sid}`。截至：{save["cutoff"]}。完整工具事件见 [trace.jsonl](trace.jsonl)。\n']
    for event in events:
        if event['type'] == 'message':
            label = '用户' if event['data']['role'] == 'user' else '助手'
            conversation.extend([f'## {event["id"]}\n', f'{label} · {event["timestamp"]}\n', event['data']['text'] + '\n'])
    models = sorted({t['model'] for t in turns if t.get('model')})
    overview = ['# 测试会话\n', f'- 会话 ID：`{sid}`', f'- 目标岗位：{role_dir.name}', f'- 开始时间：{start}', f'- 本次归档截止：{save["cutoff"]}', f'- 模型：{", ".join(models) or "未知"}；逐轮信息见 run.json', f'- Harness 客户端：{meta.get("originator", "未知")}', f'- 日志记录的 CLI 版本：{meta.get("cli_version", "未知")}；桌面应用版本未知', f'- 归档时 Git commit：{head or "未知"}', f'- 技能文件未提交修改：{save["skill_files_dirty_at_save"]}', f'- 已导出事件：{len(events)}；尚未写完整的尾部字节：{pending}', '\n## 任务\n', *[f'- {t}' for t in manifest['tasks']], '\n## 文件\n', '- [对话阅读视图](conversation.md)', '- [会话记录](trace.jsonl)', '- [运行信息与历次归档](run.json)', '\n## 记录范围\n', '保存源日志中的用户与助手可见文本、工具调用及结果、逐轮模型与可取得的配置。内部推理、系统与开发者消息、压缩摘要不导出；非文本媒体保留占位。未知或未保存到源日志的内容不补写。', '\n技能快照仅代表各次归档时的内容，保留多次快照。会话开始时日志记录的 Git 信息另存，技能早期实际版本仍需对应依据。反馈等人工备注请放在独立文件中，以上生成文件会在再次归档时更新。\n']
    atomic_write(output / 'trace.jsonl', trace.encode())
    atomic_write(output / 'conversation.md', ('\n'.join(conversation) + '\n').encode())
    atomic_write(output / 'run.md', ('\n'.join(overview) + '\n').encode())
    atomic_write(manifest_path, json_bytes(manifest))
    return output, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Exact rollout JSONL selected for this conversation')
    parser.add_argument('--repo', type=Path, required=True, help='Skill repository to snapshot')
    parser.add_argument('--role-dir', type=Path, required=True, help='Existing role directory; writes only its runs/ subdirectory')
    parser.add_argument('--session-id', help='Verify source belongs to this conversation')
    parser.add_argument('--task', required=True, help='Brief task description; does not replace earlier descriptions')
    parser.add_argument('--skill-used', action='append', default=[], help='Known skill used; repeat as needed, otherwise usage stays unknown')
    parser.add_argument('--learning-dir', type=Path)
    args = parser.parse_args()
    try:
        output, manifest = archive(args.source, args.repo, args.role_dir, args.task, args.session_id, args.skill_used, args.learning_dir)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'无法归档：{exc}\n')
    print(json.dumps({'run_dir': str(output), 'session_id': manifest['session_id'], 'saved_events': manifest['saves'][-1]['event_count'], 'archives': len(manifest['saves'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
