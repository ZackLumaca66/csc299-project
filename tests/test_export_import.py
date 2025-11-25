import json, os
from pkms_core.cli import main
from pkms_core.core import TaskManager
from pkms_core.storage import add_note, list_notes


def test_export_import_roundtrip(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    # create data
    tm = TaskManager(backend='json')
    t1 = tm.add('Exported task one', priority=4, tags=['a','b'])
    t2 = tm.add('Exported task two', priority=2, tags=['c'])
    n1 = add_note('json', str(tmp_path), 'Exported note one')
    # export
    out_file = str(tmp_path / 'backup.json')
    main(['export', out_file])
    assert os.path.exists(out_file)
    data = json.loads(open(out_file,'r',encoding='utf-8').read())
    assert 'tasks' in data and 'notes' in data
    # remove existing stores (simulate reset)
    data_dir = os.path.join(str(tmp_path), 'app_data')
    if os.path.exists(data_dir):
        for f in os.listdir(data_dir):
            os.remove(os.path.join(data_dir, f))
    # import
    main(['import', out_file])
    # verify counts restored
    tm2 = TaskManager(backend='json')
    tasks = tm2.list()
    notes = list_notes('json', str(tmp_path))
    assert len(tasks) >= 2
    assert len(notes) >= 1
