import os
from dataclasses import dataclass
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def local_environment():
    values={}
    for name in ('.env.local','backend/.env'):
        path=ROOT/name
        if path.exists():
            for line in path.read_text(encoding='utf-8-sig').splitlines():
                if '=' in line and not line.lstrip().startswith('#'):
                    key,value=line.split('=',1);values[key.strip()]=value.strip().strip('"\'')
    return {**values,**os.environ}


@dataclass(frozen=True)
class Settings:
    supabase_url:str=''
    supabase_key:str=''
    origins:tuple=('http://localhost:5173','http://127.0.0.1:5173','http://127.0.0.1:4173')

    @classmethod
    def load(cls):
        env=local_environment()
        return cls(env.get('SUPABASE_URL',env.get('VITE_SUPABASE_URL','')),
                   env.get('SUPABASE_PUBLISHABLE_KEY',env.get('VITE_SUPABASE_PUBLISHABLE_KEY','')),
                   tuple(v.strip() for v in env.get('API_CORS_ORIGINS',','.join(cls.origins)).split(',') if v.strip()))
