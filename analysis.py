import pandas as pd
from alley import Experiment
import sys
import subprocess
import os



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


def transform_ret(ret, params): # at least 1 other agent says about them that they were at CS/had alibi.
    ag_list = []
    run_num = 0
    witness_threshold = 0
    
    #df = pd.DataFrame(ag_list, columns=["run", "agentID"])
    
    header_columns = ["run", "agentID"]
    for i in range(1, 4):
        header_columns.append(f"at_least_{i}_cs_witness")
        header_columns.append(f"at_least_{i}_alibi_witness")


    for x in ret:#per run
        d_cs = {}
        d_al = {}

        for i in range(0, 10):   # num agents
            d_cs[i] = 0
            d_al[i] = 0

        for run in x:
            #print(run)
            run_num = run[0]
            if run[5] == 1:
                if run[1] != run[2]:    # no self incrimination
                    d_cs[run[2]] += 1  # agent
            if run[6] == 1:
                d_al[run[2]] += 1

        #print(run_num)
        
        for i in d_cs.keys():
            l_list = [run_num, i]
            #print(f"{i} was seen by {d_cs[i]} agents at crime scene")
            #print(f"{i} was seen by {d_al[i]} agents away from crime scene")
            for witness_threshold in range(1, 4):
                if d_cs[i] >= witness_threshold:
                    cs_witness = 1
                else:
                    cs_witness = 0
                if d_al[i] >= witness_threshold:
                    alibi_witness = 1
                else:
                    alibi_witness = 0
                l_list.append(cs_witness)
                l_list.append(alibi_witness)
                print("witnesses")
                print(l_list)
    
            ag_list.append(l_list)
    
    print(ag_list)

    df = pd.DataFrame(ag_list, columns=header_columns)
    df.to_csv(f'out/data/witness{params["experiment_name"]}.csv')



def merge_attempt(agent_type):
    df1 = pd.read_csv(f'out/data/{agent_type}.csv')
    df2 = pd.read_csv(f'out/data/witness{agent_type}.csv')
    r = pd.merge(df1, df2, on=["run", "agentID"], how='outer')
    r.to_csv(f'out/data/merge{agent_type}.csv')


def perform_experiment(agent_type):
    runs = 10
    for i in range(0, 1):
        e = Experiment(run=runs, suspect=agent_type)
        params = {"experiment_name": agent_type, "runs":runs}
        export_to_df(e,params)
        transform_ret(e.r, params)
        print(e.headings)
        e.print_table()


def calculate_LR(df, evidence, hypothesis):
    H = len(df[df[hypothesis] == 1])
    notH = len(df[df[hypothesis] == 0])
    EandH = len(df[(df[hypothesis] == 1) & (df[evidence] == 1)])
    EandnotH = len(df[(df[hypothesis] == 0) & (df[evidence] == 1)])
    P_eh = EandH / H
    P_en = EandnotH / notH
    if P_en == 0:
        P_en = 0.00000001
    LR = P_eh/P_en
    return LR

def calculate_Odds(df, evidence, hypothesis):
    H = len(df[df[hypothesis] == 1])/(len(df[df[hypothesis] == 1]) + len(df[df[hypothesis] == 0]))
    notH = len(df[df[hypothesis] == 0])/(len(df[df[hypothesis] == 1]) + len(df[df[hypothesis] == 0]))
    EandH = len(df[(df[hypothesis] == 1) & (df[evidence] == 1)])
    EandnotH = len(df[(df[hypothesis] == 0) & (df[evidence] == 1)])
    P_eh = EandH / H
    P_en = EandnotH / notH
    if P_en == 0:
        P_en = 0.001
    LR = P_eh / P_en
    odds = LR * (H/notH)
    #print(f"prior {hypothesis} == {H}, complement == {notH}")
    #print(f"P_eh = {P_eh}, P_en = {P_en}, LR = {LR}")
    #print(f"posterior {hypothesis} given {evidence} == {odds/(1+odds)}")
    print(f"change {hypothesis} given {evidence}: prior {H} to posterior {odds/(1+odds)} = {(odds/(1+odds)) - H}")
    return odds


'''def posterior(df, evidence, hypothesis):
    x = calculate_Odds(df, evidence, hypothesis)
    print(f"posterior {hypothesis} given {evidence} == {x/(1+x)}")
    return x/(1+x)

def calculate_prior(df, hypothesis):
    H = len(df[df[hypothesis] == 1]) / (len(df[df[hypothesis] == 1]) + len(df[df[hypothesis] == 0]))
    notH = len(df[df[hypothesis] == 0]) / (len(df[df[hypothesis] == 1]) + len(df[df[hypothesis] == 0]))
    print(f"prior {hypothesis} == {H}, complement == {notH}")'''

def calculate_LRs(agent_type):
    df = pd.read_csv(f'out/data/{agent_type}.csv')
    LR_dna = calculate_LR(df, "DNAatCS", "suspect")
    LR_statement = calculate_LR(df, "statement", "locCS")
    df = pd.read_csv(f'out/data/r.csv')
    LR_witness= calculate_LR(df, "other_cs", "other_suspect")
    LR_alibi = calculate_LR(df, "other_alib", "other_suspect")
    return LR_dna, LR_statement, LR_witness, LR_alibi

def calculate_all_odds(agent_type):
    df = pd.read_csv(f'out/data/{agent_type}.csv')
    dna = calculate_Odds(df, "DNAatCS", "suspect")
    statement = calculate_Odds(df, "statement", "locCS")
    df = pd.read_csv(f'out/data/r.csv')
    witness= calculate_Odds(df, "other_cs", "other_suspect")
    alibi = calculate_Odds(df, "other_alib", "other_suspect")
    return dna, statement, witness, alibi

def change(df, evidence, hypothesis):
    H = len(df[df[hypothesis] == 1])/(len(df[df[hypothesis] == 1]) + len(df[df[hypothesis] == 0]))
    notH = len(df[df[hypothesis] == 0])/(len(df[df[hypothesis] == 1]) + len(df[df[hypothesis] == 0]))
    EandH = len(df[(df[hypothesis] == 1) & (df[evidence] == 1)])
    EandnotH = len(df[(df[hypothesis] == 0) & (df[evidence] == 1)])
    P_eh = EandH / H
    P_en = EandnotH / notH
    if P_en == 0:
        P_en = 0.001
    LR = P_eh / P_en
    odds = LR * (H/notH)
    #print(f"prior {hypothesis} == {H}, complement == {notH}")
    #print(f"P_eh = {P_eh}, P_en = {P_en}, LR = {LR}")
    #print(f"posterior {hypothesis} given {evidence} == {odds/(1+odds)}")
    p = odds/(1+odds)
    print(f"change {hypothesis} given {evidence}: prior {H} to posterior {p} = {p - H}")
    return H, p


def calculate_change(agent_type, run):
    df = pd.read_csv(f'out/data/merge{agent_type}.csv')
    l = [("DNAatCS", "suspect"), ("statement", "locCS")]
    for i in range(1, 4):   # witness_threshold
         l.append((f"at_least_{i}_cs_witness", "suspect"))
         l.append((f"at_least_{i}_alibi_witness", "suspect"))

    st = []
    for (ev, hyp) in l:
        H, p = change(df, ev, hyp)
        c = p-H
        x = [run, hyp, ev, H, p, c] # f"change {hyp} given {ev}: prior {H} to posterior {p} = {c}
        st.append(x)
    return st

l = []
l_i = []
for i in range(0, 2):
    perform_experiment("thief")
    merge_attempt("thief")
    t = calculate_change("thief", i)
    l = l + t

    perform_experiment("innocent")
    merge_attempt("innocent")
    t = calculate_change("innocent", i)
    l_i = l_i + t

df = pd.DataFrame(l, columns=["run", "hyp", "ev", "H", "p", "c"])
df.to_csv("out/data/outputthief.csv")

df = pd.DataFrame(l_i, columns=["run", "hyp", "ev", "H", "p", "c"])
df.to_csv("out/data/outputinnocent.csv")

os.system("Rscript generatingNetworkAlleys.R")


