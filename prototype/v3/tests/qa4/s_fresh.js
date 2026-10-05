V3_SCEN.example(); ACT.v3own(); $('#phrase').value = 'Кофемашина 30 тысяч к 1 марта, плачу сам'; ACT.phraseGo(); ACT.v3save(); ACT.v3alone(); await new Promise(r => setTimeout(r, 700)); return 1;
