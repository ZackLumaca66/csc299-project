from __future__ import annotations
import argparse, sys, os
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
    p = argparse.ArgumentParser(prog='pkms', description='Task & PKMS CLI (prototype)', epilog='Examples: pkms add "Buy milk"; pkms advise; pkms dashboard')
    sub = p.add_subparsers(dest='command')
    # task commands
    add_p = sub.add_parser('add', help='add a task'); add_p.add_argument('text'); add_p.add_argument('--backend', choices=['json','sqlite'])
    list_p = sub.add_parser('list', help='list tasks'); list_p.add_argument('--backend', choices=['json','sqlite'])
    search_p = sub.add_parser('search', help='search tasks'); search_p.add_argument('query'); search_p.add_argument('--backend', choices=['json','sqlite'])
    toggle_p = sub.add_parser('toggle', help='toggle task'); toggle_p.add_argument('id', type=int); toggle_p.add_argument('--backend', choices=['json','sqlite'])
    del_p = sub.add_parser('delete', help='delete task'); del_p.add_argument('id', type=int); del_p.add_argument('--backend', choices=['json','sqlite'])
    exp_p = sub.add_parser('export', help='export tasks'); exp_p.add_argument('path'); exp_p.add_argument('--backend', choices=['json','sqlite'])
    # doc commands
    doc_add = sub.add_parser('doc-add', help='add document'); doc_add.add_argument('title'); doc_add.add_argument('text'); doc_add.add_argument('--tags', default=''); doc_add.add_argument('--backend', choices=['json','sqlite'])
    doc_list = sub.add_parser('doc-list', help='list documents'); doc_list.add_argument('--backend', choices=['json','sqlite'])
    doc_search = sub.add_parser('doc-search', help='search documents'); doc_search.add_argument('query'); doc_search.add_argument('--backend', choices=['json','sqlite'])
    doc_view = sub.add_parser('doc-view', help='view document'); doc_view.add_argument('id', type=int); doc_view.add_argument('--backend', choices=['json','sqlite'])
    doc_del = sub.add_parser('doc-delete', help='delete document'); doc_del.add_argument('id', type=int); doc_del.add_argument('--backend', choices=['json','sqlite'])
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
    chat_suggest = sub.add_parser('chat-suggest', help='suggest tasks from documents'); chat_suggest.add_argument('--backend', choices=['json','sqlite'])
    advise_p = sub.add_parser('advise', help='show productivity advice'); advise_p.add_argument('--backend', choices=['json','sqlite'])
    dash_p = sub.add_parser('dashboard', help='show dashboard summary'); dash_p.add_argument('--backend', choices=['json','sqlite'])
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
    if llm.available():
        logger.info('LLM adapter active (key detected).')
        say('LLM adapter active (key detected).', style='green')
    else:
        logger.info('LLM adapter inactive (no key found).')
        say('LLM adapter inactive (no key found).', style='yellow')
    agent = Agent(llm=llm)
    history = ChatHistory.load()
    chat_engine = ChatEngine(agent, tm, dm, history)
    cmd = args.command
    if cmd == 'add':
        t = tm.add(args.text); say(f"added task {t.id}: {t.text}", style='cyan')
    elif cmd == 'list':
        for t in tm.list(): say(f"[{ 'x' if t.completed else ' '}] {t.id}: {t.text}")
    elif cmd == 'search':
        for t in tm.search(args.query): print(f"{t.id}: {t.text}")
    elif cmd == 'toggle':
        t = tm.toggle(args.id); print('not found' if not t else f"toggled {t.id}: {'completed' if t.completed else 'pending'}")
    elif cmd == 'delete':
        ok = tm.delete(args.id); print('deleted' if ok else 'not found')
    elif cmd == 'export':
        tm.export(args.path); say(f"exported to {args.path}")
    elif cmd == 'doc-add':
        tags = [t.strip() for t in args.tags.split(',') if t.strip()] if args.tags else []
        d = dm.add(args.title, args.text, tags=tags); say(f"added doc {d.id}: {d.title}", style='cyan')
    elif cmd == 'doc-list':
        for d in dm.list(): say(f"{d.id}: {d.title} [tags: {', '.join(d.tags)}]")
    elif cmd == 'doc-search':
        for d in dm.search(args.query): print(f"{d.id}: {d.title}")
    elif cmd == 'doc-view':
        d = dm.get(args.id); print('not found' if not d else f"{d.id}: {d.title}\n----\n{d.text}\n----\ntags: {', '.join(d.tags)}")
    elif cmd == 'doc-delete':
        ok = dm.delete(args.id); print('deleted' if ok else 'not found')
    elif cmd == 'chat':
        # normalize message (args.message may be list)
        msg = None
        if isinstance(args.message, (list, tuple)) and len(args.message) > 0:
            msg = ' '.join(args.message).strip()
        elif isinstance(args.message, str) and args.message:
            msg = args.message

        # handle selection flags
        if args.task_id:
            ok = chat_engine.select_task(args.task_id)
            if ok:
                say(f"Selected task {args.task_id}", style='cyan')
            else:
                say(f"Task {args.task_id} not found", style='red')
        elif args.select:
            # prompt user to select from list
            tasks = tm.list()
            if not tasks:
                say('No tasks available to select', style='yellow')
            else:
                say('Tasks:')
                for t in tasks: say(f"{t.id}: {t.text}")
                try:
                    pick = input('Select task id (or blank to cancel): ').strip()
                    if pick:
                        tid = int(pick)
                        ok = chat_engine.select_task(tid)
                        say('selected' if ok else 'not found')
                except Exception:
                    say('invalid selection', style='red')

        # single-message mode
        if msg and not args.interactive:
            response = chat_engine.handle_message(msg)
            say(response)
            history.save()
        else:
            # interactive chat loop
            say("Entering interactive chat. Commands: /select <id>, /clear, /exit, /help")
            while True:
                try:
                    line = input('chat> ').strip()
                except (EOFError, KeyboardInterrupt):
                    print() ; break
                if not line: continue
                if line in {'/exit','exit','quit'}: break
                if line in {'/help','help'}:
                    say("Commands: /select <id>, /clear, /exit, /help. You can also type 'summarize task <id>' or 'suggest tasks'.")
                    continue
                if line.startswith('/select '):
                    try:
                        tid = int(line.split()[1]); ok = chat_engine.select_task(tid)
                        say(f"selected {tid}" if ok else 'not found')
                    except Exception:
                        say('bad id', style='red')
                    continue
                if line.startswith('/clear'):
                    chat_engine.clear_selection(); say('selection cleared'); continue
                resp = chat_engine.handle_message(line)
                say(resp)
                history.save()
    elif cmd == 'chat-history':
        for entry in history.entries:
            say(f"{entry['role']}: {entry['text']}")
    elif cmd == 'chat-suggest':
        suggestions = agent.suggest_tasks_from_documents(dm.list())
        for s in suggestions: say(f"- {s}")
    elif cmd == 'advise':
        advice = agent.productivity_advice(tm.list(), dm.list())
        for line in advice: say(line)
    elif cmd == 'dashboard':
        from .dashboard import show_dashboard
        show_dashboard(tm.list(), dm.list(), agent)
    elif cmd == 'info':
        # Display helpful environment and data path information
        say(f"cwd: {os.getcwd()}")
        store = getattr(tm, 'store', None)
        dstore = getattr(dm, 'store', None)
        backend_name = getattr(store, 'path', None)
        say(f"task store: {getattr(store, 'path', repr(store))}")
        say(f"document store: {getattr(dstore, 'path', repr(dstore))}")
        say(f"active backend: {args.backend}")
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
                print("Commands: add, list, search, toggle, delete, doc-add, doc-list, doc-search, doc-view, chat msg, advise, dashboard")
                continue
            if line.startswith('add '):
                t = tm.add(line[4:]); print(f"added task {t.id}") ; continue
            if line.startswith('search '):
                for t in tm.search(line[7:]): print(f"{t.id}: {t.text}") ; continue
            if line.startswith('toggle '):
                try: tid=int(line.split()[1]); t=tm.toggle(tid); print('ok' if t else 'not found')
                except Exception: print('bad id') ; continue
            if line.startswith('doc-add '):
                # simple pattern: doc-add Title | Text
                payload = line[8:]
                if '|' in payload:
                    title,text = [p.strip() for p in payload.split('|',1)]
                    d = dm.add(title,text, tags=[]); print(f"doc {d.id} added")
                else:
                    print('Usage: doc-add Title | Text')
                continue
            if line.startswith('doc-search '):
                for d in dm.search(line[11:]): print(f"{d.id}: {d.title}") ; continue
            if line.startswith('doc-view '):
                try: did=int(line.split()[1]); d=dm.get(did); print(d.title if d else 'not found')
                except Exception: print('bad id') ; continue
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
    else:
        print('unknown command'); return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
