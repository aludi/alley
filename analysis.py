import pandas as pd
from alley import Experiment



def export_to_df(e, params):
    df_list = []
    for x in e.total_states:
        d = pd.DataFrame(x, columns=e.headings)
        df_list.append(d)
    df = pd.concat(df_list)
    experiment_name = params["experiment_name"]
    for name, value in params.items():
        df[name] = value
    df.to_csv(f'out/data/{experiment_name}.csv')


def export_ret(r):
    df_list = []
    for x in r:
        d = pd.DataFrame(x, columns= ["own", "other", "thief", "suspect", "cs", "alib"])
        df_list.append(d)
    df = pd.concat(df_list)
    df.to_csv(f'out/data/r.csv')


def perform_experiment():
    runs = 50
    for i in range(0, 1):
        e = Experiment(run=runs, suspect="thief")
        params = {"experiment_name": "thief", "runs":runs}
        export_to_df(e,params)
        export_ret(e.r)
        '''e1 = Experiment(run=runs, suspect="innocent")
        params = {"experiment_name": "innocent", "runs":runs}
        export_to_df(e1, params)'''

        print(e.headings)
        e.print_table()
        #e1.print_table()

def calculate_LRs_witness():
    df = pd.read_csv(f'out/data/r.csv')
    p_thief = len(df[df["suspect"] == 1])/(len(df[df["suspect"] == 1]) + len(df[df["suspect"] == 0]))
    p_not_thief = len(df[df["suspect"] == 0])/(len(df[df["suspect"] == 1]) + len(df[df["suspect"] == 0]))

    print(p_thief, p_not_thief)

    saw_x_and_x_thief = len(df[(df.cs == 1) & (df.suspect == 1)])
    saw_x_and_x_not_thief = len(df[(df.cs == 1) & (df.suspect == 0)])

    thief = len(df[df["suspect"] == 1])
    not_thief = len(df[df["suspect"] == 0])

    print(saw_x_and_x_thief, saw_x_and_x_not_thief)
    print(saw_x_and_x_thief/thief, saw_x_and_x_not_thief/not_thief)
    print(f"LR witness : {(saw_x_and_x_thief/thief)/(saw_x_and_x_not_thief/not_thief)}")

    alibi_x_and_x_thief = len(df[(df.alib == 1) & (df.thief == 1)])
    alibi_x_and_x_not_thief = len(df[(df.alib == 1) & (df.thief == 0)])

    print(alibi_x_and_x_thief, saw_x_and_x_not_thief)
    print(alibi_x_and_x_not_thief / thief, saw_x_and_x_not_thief / not_thief)
    print(f"LR alibi: {(alibi_x_and_x_thief / thief) / (alibi_x_and_x_not_thief / not_thief)}")

    LRwit = (saw_x_and_x_thief/thief)/(saw_x_and_x_not_thief/not_thief)
    LRal = (alibi_x_and_x_thief / thief) / (alibi_x_and_x_not_thief / not_thief)
    return LRwit, LRal



def calculate_LR(df, evidence, hypothesis):
    H = len(df[df[hypothesis] == 1])
    notH = len(df[df[hypothesis] == 0])
    EandH = len(df[(df[hypothesis] == 1) & (df[evidence] == 1)])
    EandnotH = len(df[(df[hypothesis] == 0) & (df[evidence] == 0)])
    P_eh = EandH / H
    P_en = EandnotH / notH
    LR = P_eh/P_en
    return LR

def calculate_LRs(agent_type):
    df = pd.read_csv(f'out/data/{agent_type}.csv')
    LR_dna = calculate_LR(df, "DNAatCS", "suspect")
    LR_statement = calculate_LR(df, "statement", "locCS")
    df = pd.read_csv(f'out/data/r.csv')
    LR_witness= calculate_LR(df, "cs", "suspect")
    LR_alibi = calculate_LR(df, "alib", "suspect")
    return LR_dna, LR_statement, LR_witness, LR_alibi



def calculate_LRs_old(agent_type):
    df = pd.read_csv(f'out/data/{agent_type}.csv')

    locCS = len(df[df["suspect"] == 1])
    NotlocCS = len(df[df["suspect"] == 0])
    stat_locCS = len(df[(df["suspect"] == 1) & (df["DNAatCS"] == 1)])
    stat_NotlocCS = len(df[(df["suspect"] == 0) & (df["DNAatCS"] == 0)])
    P_eh = stat_locCS / locCS
    P_en = stat_NotlocCS / NotlocCS
    print(locCS, NotlocCS, stat_locCS, stat_NotlocCS, P_eh, P_en)
    print(f"LR dna {P_eh / P_en}")
    d = P_eh / P_en


    locCS = len(df[df["locCS"] == 1])
    NotlocCS = len(df[df["locCS"] == 0])
    stat_locCS = len(df[(df.locCS == 1) & (df.statement == 1)])
    stat_NotlocCS = len(df[(df.locCS == 0) & (df.statement == 0)])
    P_eh = stat_locCS/locCS
    P_en = stat_NotlocCS/NotlocCS
    print(locCS, NotlocCS, stat_locCS, stat_NotlocCS, P_eh, P_en)
    print(f"LR statement {P_eh/P_en}")
    s = P_eh/P_en

    return d, s




l = []
for i in range(0, 5):
    #perform_experiment()
    #w, a = calculate_LRs_witness()
    d, s, w, a = calculate_LRs("thief")
    l.append((d, s, w, a))

for d, s, w, a in l:
    print(f"LR DNA {d}, LR stat {s} LR witness {w}, LR alibi {a}")
#calculate_LRs("thief")
#calculate_LRs("innocent")
