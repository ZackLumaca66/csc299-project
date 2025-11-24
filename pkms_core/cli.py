from __future__ import annotations
import argparse, sys, os, shutil
from .core import TaskManager, DocumentManager
from .chat import ChatHistory, ChatEngine
from .agent import Agent
from .llm import LLMAdapter
from .logging_setup import init_logging

# Optional rich Console for nicer CLI output
try:
    from rich.console import Console
    console = Console()
except Exception:
    console = None

def say(msg, style=None):
    if console:
        console.print(msg, style=style)
    else:
        print(msg)

def build_parser():
    p = argparse.ArgumentParser(prog='pkms', description='Task & PKMS CLI', epilog='Examples: pkms add "Buy milk"; pkms advise; pkms dashboard')
    sub = p.add_subparsers(dest='command')
    # task commands
    add_p = sub.add_parser('add', help='add a task'); add_p.add_argument('text'); add_p.add_argument('--backend', choices=['json','sqlite'])
    edit_p = sub.add_parser('edit', help='edit a task'); edit_p.add_argument('id', type=int); edit_p.add_argument('text'); edit_p.add_argument('--backend', choices=['json','sqlite'])
    list_p = sub.add_parser('list', help='list tasks (dashboard)'); list_p.add_argument('--backend', choices=['json','sqlite'])
    describe_p = sub.add_parser('describe', help='add a detail bullet to a task'); describe_p.add_argument('id', type=int); describe_p.add_argument('detail', nargs='+')
    complete_p = sub.add_parser('complete', help='mark a task completed (adds a checkmark)'); complete_p.add_argument('id', type=int); complete_p.add_argument('--backend', choices=['json','sqlite'])
    search_p = sub.add_parser('search', help='search tasks'); search_p.add_argument('query'); search_p.add_argument('--backend', choices=['json','sqlite'])
    del_p = sub.add_parser('delete', help='delete task'); del_p.add_argument('id', type=int); del_p.add_argument('--backend', choices=['json','sqlite'])
    # export and doc commands removed per user request
    p.add_argument('--backend', choices=['json','sqlite'], default='json', help='task storage backend')
    p.add_argument('--verbose', action='store_true', help='enable verbose logging')
    # chat commands
    chat_p = sub.add_parser('chat', help='chat with the advisor (single message or interactive)')
    chat_p.add_argument('message', nargs='*', help='optional message; if omitted runs interactive chat')
    chat_p.add_argument('--task-id', type=int, help='task id to attach to this chat session')
    chat_p.add_argument('--select', action='store_true', help='prompt to select a task before chatting')
    chat_p.add_argument('--interactive', action='store_true', help='force interactive chat session')
    chat_p.add_argument('--backend', choices=['json','sqlite'])
    chat_history = sub.add_parser('chat-history', help='show chat history'); chat_history.add_argument('--backend', choices=['json','sqlite'])
    # chat-suggest removed per user request
    advise_p = sub.add_parser('advise', help='show productivity advice'); advise_p.add_argument('--backend', choices=['json','sqlite'])
    dash_p = sub.add_parser('dashboard', help='show dashboard summary')
    dash_p.add_argument('--backend', choices=['json','sqlite'])
    dash_p.add_argument('--interactive', action='store_true', help='open interactive TUI dashboard')
    sub.add_parser('home', help='show a friendly home screen with quick commands')
    setup_p = sub.add_parser('setup-llm', help='configure OpenAI API key for LLM usage (stores in OS keyring)')
    setup_p.add_argument('--remove', action='store_true', help='remove stored API key')
    setup_p.add_argument('--show', action='store_true', help='show whether a key is stored (masked)')
    # reset command: wipe app data
    reset_p = sub.add_parser('reset', help='wipe all app data (tasks, docs, chat history)')
    reset_p.add_argument('--yes', action='store_true', help='confirm destructive reset')
    sub.add_parser('instructions', help='show detailed instructions and examples for all commands')
    shell_p = sub.add_parser('shell', help='interactive shell (enter commands or chat messages)'); shell_p.add_argument('--backend', choices=['json','sqlite'])
    sub.add_parser('info', help='show environment and data paths')
    return p

def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = build_parser(); args = parser.parse_args(argv)
    if not args.command:
        parser.print_help(); return 0
    logger = init_logging(args.verbose)
    tm = TaskManager(backend=args.backend)
    dm = DocumentManager()
    llm = LLMAdapter()
    agent = Agent(llm=llm)
    # Only show LLM availability messages on verbose mode or when running chat/home/advise commands
    if args.verbose or args.command in {'chat', 'home', 'advise'}:
        if llm.available():
            logger.info('LLM adapter active (key detected).')
            say('LLM adapter active (key detected).', style='green')
        else:
            logger.info('LLM adapter inactive (no key found).')
            say('LLM adapter inactive (no key found).', style='yellow')
    history = ChatHistory.load()
    chat_engine = ChatEngine(agent, tm, dm, history)
    cmd = args.command
    # note: removed ls/db/complete aliases per user request
    if cmd == 'add':
        t = tm.add(args.text); say(f"added task {t.id}: {t.text}", style='cyan')
    elif cmd == 'edit':
        # interpret numeric id as list-number (1-based); fail if out of range
        try:
            supplied = int(args.id)
            tasks = tm.list()
            if 1 <= supplied <= len(tasks):
                real_id = tasks[supplied-1].id
            else:
                say('task not found', style='red')
                return 0
        except Exception:
            say('invalid id', style='red')
            return 0
        t = tm.edit(real_id, args.text)
        say(f"edited task {supplied}: {t.text}" if t else "task not found", style='cyan')
    elif cmd == 'list':
        # Use the dashboard view for listing tasks for a consistent UI
        from .dashboard import show_dashboard
        show_dashboard(tm.list(), dm.list(), agent)
    elif cmd == 'search':
        for t in tm.search(args.query): print(f"{t.id}: {t.text}")
    elif cmd == 'delete':
        try:
            supplied = int(args.id)
            tasks = tm.list()
            if 1 <= supplied <= len(tasks):
                real_id = tasks[supplied-1].id
            else:
                print('not found'); return 0
        except Exception:
            print('invalid id'); return 0
        ok = tm.delete(real_id); print('deleted' if ok else 'not found')
    elif cmd == 'describe':
        text = ' '.join(args.detail).strip()
        try:
            supplied = int(args.id)
            tasks = tm.list()
            if 1 <= supplied <= len(tasks):
                real_id = tasks[supplied-1].id
            else:
                say('task not found', style='red'); return 0
        except Exception:
            say('invalid id', style='red'); return 0
        t = tm.add_detail(real_id, text)
        say(f"added detail to {supplied}" if t else "task not found")
    elif cmd == 'complete':
        try:
            supplied = int(args.id)
            tasks = tm.list()
            if 1 <= supplied <= len(tasks):
                real_id = tasks[supplied-1].id
            else:
                say('task not found', style='red')
                return 0
        except Exception:
            say('invalid id', style='red'); return 0
        t = tm.set_completed(real_id, True)
        say(f"completed task {supplied}: {t.text}" if t else 'task not found', style='green')
    # export and doc commands removed per user request
    elif cmd == 'chat':
        # normalize message (args.message may be list)
        msg = None
        if isinstance(args.message, (list, tuple)) and len(args.message) > 0:
            msg = ' '.join(args.message).strip()
        elif isinstance(args.message, str) and args.message:
            msg = args.message

        def _is_advise_message(text: str):
            if not text:
                return None
            t = text.strip().lower()
            if t in {'advise', 'advise all', 'advice', 'advise all please'}:
                return ('all', None)
            if t.startswith('advise selected'):
                parts = t.split()
                if len(parts) == 2:
                    return ('selected', None)
                try:
                    idx = int(parts[-1])
                    return ('selected', idx)
                except Exception:
                    return None
            return None

        # handle selection flags
        if args.task_id is not None:
            # treat provided task_id as list-number (1-based)
            try:
                supplied = int(args.task_id)
                tasks = tm.list()
                if 1 <= supplied <= len(tasks):
                    real_id = tasks[supplied-1].id
                    ok = chat_engine.select_task(real_id)
                    say(f"Selected task {supplied}", style='cyan')
                else:
                    say(f"Task {args.task_id} not found", style='red')
            except Exception:
                say('invalid task id', style='red')
                if args.select:
                    # prompt user to select from list
                    tasks = tm.list()
                    if not tasks:
                        say('No tasks available to select', style='yellow')
                    else:
                        say('Tasks:')
                        for idx, t in enumerate(tasks, start=1):
                            say(f"{idx}. {t.text}")
                        try:
                            pick = input('Select task number (or blank to cancel): ').strip()
                            if pick:
                                tid = int(pick)
                                if 1 <= tid <= len(tasks):
                                    ok = chat_engine.select_task(tasks[tid-1].id)
                                    say('selected' if ok else 'not found')
                                else:
                                    say('not found', style='red')
                        except Exception:
                            say('invalid selection', style='red')

        # single-message mode: accept only advise commands
        if msg and not args.interactive:
            parsed = _is_advise_message(msg)
            if not parsed:
                say('Chat only accepts: "advise all" or "advise selected <n>"', style='yellow')
            else:
                kind, idx = parsed
                if kind == 'all':
                    response = chat_engine.handle_message('advise')
                else:
                    # selected: prefer explicit index from message, fall back to --task-id
                    use_idx = idx
                    if use_idx is None and args.task_id is not None:
                        use_idx = args.task_id
                    if use_idx is None:
                        say('advise selected requires a task number (e.g. "advise selected 1") or --task-id', style='red')
                        history.save()
                    else:
                        # resolve list-number to real id
                        try:
                            tasks = tm.list()
                            if 1 <= int(use_idx) <= len(tasks):
                                chat_engine.select_task(tasks[int(use_idx)-1].id)
                                # trigger contextual reply by sending empty message
                                response = chat_engine.handle_message('')
                            else:
                                response = 'Task not found'
                        except Exception:
                            response = 'Invalid task number'
                try:
                    say(response)
                except UnboundLocalError:
                    pass
                history.save()
        else:
            # interactive chat loop constrained to advise commands
            say('Entering interactive chat. Commands: advise all | advise selected <n> | /exit', style='bold')
            while True:
                try:
                    line = input('chat> ').strip()
                except (EOFError, KeyboardInterrupt):
                    print() ; break
                if not line: continue
                if line in {'/exit','exit','quit'}: break
                if line.lower().startswith('advise'):
                    parsed = _is_advise_message(line)
                    if not parsed:
                        say('Use: advise all or advise selected <n>', style='yellow'); continue
                    kind, idx = parsed
                    if kind == 'all':
                        resp = chat_engine.handle_message('advise')
                    else:
                        if idx is None:
                            say('Specify task number: advise selected <n>', style='yellow'); continue
                        tasks = tm.list()
                        if 1 <= idx <= len(tasks):
                            chat_engine.select_task(tasks[idx-1].id)
                            resp = chat_engine.handle_message('')
                        else:
                            resp = 'Task not found'
                    say(resp)
                    history.save()
                    continue
                say('Only advise commands are supported in chat: advise all | advise selected <n>', style='yellow')
        for entry in history.entries:
            say(f"{entry['role']}: {entry['text']}")
    elif cmd == 'chat-history':
        for entry in history.entries:
            say(f"{entry['role']}: {entry['text']}")
    elif cmd == 'advise':
        advice = agent.productivity_advice(tm.list(), dm.list())
        for line in advice: say(line)
    elif cmd == 'dashboard':
        # Default to tasks-only dashboard for CLI users (no docs/advice/suggestions)
        if getattr(args, 'interactive', False):
            try:
                from .tui import run_tui

                run_tui(tm, dm, agent)
            except Exception:
                say('Interactive TUI not available; falling back to static dashboard', style='yellow')
                from .dashboard import show_dashboard
                show_dashboard(tm.list(), dm.list(), agent)
        else:
            from .dashboard import show_dashboard
            show_dashboard(tm.list(), dm.list(), agent)
    elif cmd == 'home':
        say('PKMS Home — quick commands', style='bold')
        say('Add, manage, and ask about tasks — concise one-line help:')

        say('  add <text>               — create a new task')
        say('  edit <n> <text>          — edit task by list-number (1-based)')
        say('  describe <n> <detail>    — add a bullet/detail to a task')
        say('  delete <n>               — remove a task by list-number')
        say('  list                    — show tasks-only dashboard')
        say('  dashboard [--interactive]— show dashboard; --interactive launches TUI when available')
        say('  chat [--task-id <n>]     — chat with the agent (advise commands only in single-message mode)')
        say('  chat-history             — display saved chat history')
        say('  advise                   — compact productivity advice')
        say('  setup-llm                — store or remove OpenAI API key (use --show or --remove)')
        say('  reset [--yes]            — DESTRUCTIVE: wipe persistent stores and chat history')
    elif cmd == 'instructions':
        say('PKMS Instructions', style='bold')
        say('A brief command reference — one-line descriptions only.', style='cyan')
        say('List numbers shown by `list` are 1-based and are the preferred identifiers.')

        say('\nadd <text>')
        say('  Create a new task with the given text.')

        say('\nedit <n> <text>')
        say('  Replace the text of task identified by list-number <n>.')

        say('\ndescribe <n> <detail>')
        say('  Append a short bullet/detail to task <n>.')

        say('\nlist')
        say('  Show the tasks-only dashboard.')

        say('\ndashboard [--interactive]')
        say('  Show dashboard; --interactive launches the TUI when available.')

        say('\nsearch <query>')
        say('  Find tasks matching the query string.')

        say('\ndelete <n>')
        say('  Permanently remove the task referenced by list-number <n>.')

        say('\nchat [message] [--task-id <n>] [--interactive]')
        say('  Chat with the agent; single-message mode accepts only advise commands; --interactive opens a constrained session.')
        say('\n  Chat examples:')
        say('    python -m pkms_core.cli chat "advise"')
        say('    python -m pkms_core.cli chat "advise selected 1"')
        say('    python -m pkms_core.cli chat --interactive  (then use: advise all | advise selected <n> | /select <n> | /exit)')

        say('\nchat-history')
        say('  Print saved chat history.')

        say('\nadvise')
        say('  Print a short productivity advice summary (heuristic + doc-derived count).')

        say('\nsetup-llm [--show|--remove]')
        say('  Store, view, or remove your OpenAI API key in the OS keyring.')

        say('\nreset [--yes]')
        say('  DESTRUCTIVE: remove all known persistent stores and chat history.')

        say('\nhome')
        say('  Print a short quick-reference of common commands.')

        say('\ninstructions')
        say('  Print this concise instructions page.')

        say('\nshell')
        say('  Start a small interactive shell for quick commands and chat.')

        say('\ninfo')
        say('  Print environment, active backend, and store file paths.')

        say('\nNotes:')
        say('  - Use list numbers (1-based) when referring to tasks.')
        say('  - Many commands accept `--backend json|sqlite` to control persistence.')
        say('  - To enable LLM features set `OPENAI_API_KEY` or run `python -m pkms_core.cli setup-llm`.')
    elif cmd == 'info':
        # Display helpful environment and data path information
        say(f"cwd: {os.getcwd()}")
        store = getattr(tm, 'store', None)
        dstore = getattr(dm, 'store', None)
        backend_name = getattr(store, 'path', None)
        say(f"task store: {getattr(store, 'path', repr(store))}")
        say(f"document store: {getattr(dstore, 'path', repr(dstore))}")
        say(f"active backend: {args.backend}")
    elif cmd == 'reset':
        # destructive: remove all known app data and legacy stores
        cwd = os.getcwd()
        dirs_to_remove = [os.path.join(cwd, 'app_data'), os.path.join(cwd, 'data_pkms'), os.path.join(cwd, 'demo_data')]
        files_to_remove = [os.path.join(cwd, 'tasks.json'), os.path.join(cwd, 'docs.json')]

        # include explicit store file paths if available (covers JsonTaskStore/SqliteTaskStore)
        try:
            if getattr(tm, 'store', None) and getattr(tm.store, 'path', None):
                files_to_remove.append(tm.store.path)
        except Exception:
            pass
        try:
            if getattr(dm, 'store', None) and getattr(dm.store, 'path', None):
                files_to_remove.append(dm.store.path)
        except Exception:
            pass

        if not getattr(args, 'yes', False):
            confirm = input("This will permanently delete app data, legacy stores, and chat history. Type YES to confirm: ").strip()
            if confirm != 'YES':
                say('Aborted.', style='yellow')
                return 0

        # remove directories
        for d in dirs_to_remove:
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                    say(f'Removed {d}', style='green')
                except Exception as e:
                    say(f'Failed to remove {d}: {e}', style='red')

        # remove files
        for f in files_to_remove:
            try:
                if f and os.path.exists(f):
                    try:
                        os.remove(f)
                        say(f'Removed {f}', style='green')
                    except IsADirectoryError:
                        # in case a dir ended up in the list
                        shutil.rmtree(f)
                        say(f'Removed directory {f}', style='green')
            except Exception as e:
                say(f'Failed to remove {f}: {e}', style='red')

        # Also attempt to remove chat history path used by ChatHistory (data_pkms/chat_history.json)
        try:
            from .chat import CHAT_HISTORY_FILE
            if os.path.exists(CHAT_HISTORY_FILE):
                os.remove(CHAT_HISTORY_FILE)
                say(f'Removed chat history {CHAT_HISTORY_FILE}', style='green')
        except Exception:
            pass

        # Clear in-memory state for this process
        try:
            if getattr(tm, 'tasks', None) is not None:
                tm.tasks = []
        except Exception:
            pass

        say('Reset complete.', style='green')
        return 0
    elif cmd == 'shell':
        print("Type '/help' for help, '/exit' to quit. Use command syntax or plain chat messages.")
        while True:
            try:
                line = input('> ').strip()
            except (EOFError, KeyboardInterrupt):
                print() ; break
            if not line: continue
            if line in {'/exit','exit','quit'}: break
            if line in {'/help','help'}:
                print("Commands: add, list, search, delete, chat msg, advise, dashboard")
                continue
            if line.startswith('add '):
                t = tm.add(line[4:]); print(f"added task {t.id}") ; continue
            if line.startswith('search '):
                for t in tm.search(line[7:]): print(f"{t.id}: {t.text}") ; continue
            # removed toggle and doc-* shell shortcuts per user request
            if line.startswith('advise'):
                for a in agent.productivity_advice(tm.list(), dm.list()): print(a); continue
            if line.startswith('dashboard'):
                from .dashboard import show_dashboard
                show_dashboard(tm.list(), dm.list(), agent); continue
            if line.startswith('/select '):
                try:
                    tid = int(line.split()[1]); ok = chat_engine.select_task(tid)
                    print(f"selected {tid}" if ok else 'not found')
                except Exception:
                    print('bad id')
                continue
            if line.strip() == '/current':
                cur = getattr(chat_engine, 'selected_task', None)
                if cur:
                    print(f"current selection: {cur.id}: {cur.text}")
                else:
                    print('no task selected')
                continue
            # chat fallback
            resp = chat_engine.handle_message(line)
            print(resp)
            history.save()
    elif cmd == 'setup-llm':
        # Configure OpenAI API key in OS keyring (optional)
        try:
            from . import keyring_store
        except Exception:
            keyring_store = None
        import getpass
        if getattr(args, 'remove', False):
            if keyring_store and keyring_store.available():
                ok = keyring_store.delete_api_key()
                say('Removed stored API key.' if ok else 'No stored key found or failed to remove.', style='green' if ok else 'yellow')
            else:
                say('Keyring not available. Set OPENAI_API_KEY in environment instead.', style='yellow')
        elif getattr(args, 'show', False):
            if keyring_store and keyring_store.available():
                k = keyring_store.get_api_key()
                if k:
                    masked = k[:4] + '...' + k[-4:]
                    say(f'Stored API key: {masked}', style='cyan')
                else:
                    say('No API key stored in keyring.', style='yellow')
            else:
                say('Keyring not available. Set OPENAI_API_KEY in environment instead.', style='yellow')
        else:
            if keyring_store and keyring_store.available():
                say('Enter your OpenAI API key (input hidden).')
                val = getpass.getpass('API key: ')
                if not val.strip():
                    say('Empty key; aborting.', style='red')
                else:
                    ok = keyring_store.set_api_key(val.strip())
                    say('Key stored in OS keyring.' if ok else 'Failed to store key (keyring error).', style='green' if ok else 'red')
            else:
                say('Keyring not available. To use LLM set the env var OPENAI_API_KEY, or install Python package "keyring" and try again.', style='yellow')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
