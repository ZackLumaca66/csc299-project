import os
from pkms_core.llm import LLMAdapter
from pkms_core.agent import Agent
from pkms_core.models import Task

def test_llm_adapter_unavailable():
    for k in ('OPENAI_KEY','OPENAI_API_KEY','ANTHROPIC_KEY'):
        if k in os.environ: del os.environ[k]
    llm = LLMAdapter()
    assert not llm.available()
    assert llm.summarize('Anything here') is None

def test_llm_adapter_available(monkeypatch):
    monkeypatch.setenv('OPENAI_KEY','dummy')
    llm = LLMAdapter()
    assert llm.available()
    out = llm.summarize('This is a long text that should be shortened by the adapter for preview purposes in interface.')
    assert '[llm]' in out
    agent = Agent(llm=llm)
    summary = agent.summarize_task(Task(id=1,text='Implement logging and llm scaffold for pkms',created='now'))
    assert '[llm]' in summary