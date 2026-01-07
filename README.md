ai_interviewer/
│
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── interview_routes.py
│   │   └── websocket_routes.py
│   │
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── question_agent.py
│   │   ├── evaluation_agent.py
│   │   ├── decision_agent.py
│   │
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── speech_service.py
│   │   ├── emotion_service.py
│   │   └── memory_service.py
│   │
│   ├── graph/
│   │   ├── interview_graph.py
│   │
│   ├── models/
│   │   ├── interview_state.py
│   │
│   ├── utils/
│   │   ├── prompts.py
│   │   └── logger.py
│
├── frontend/
│   └── react-app/
│
├── requirements.txt
└── README.md
