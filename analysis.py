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


def export_ret(r):
    df_list = []
    for x in r:
        d = pd.DataFrame(x, columns= ["run", "agentID", "other", "other_thief", "other_suspect", "other_cs", "other_alib"])
        df_list.append(d)
    df = pd.concat(df_list)
    df.to_csv(f'out/data/r.csv')

def merge_attempt():
    df1 = pd.read_csv(f'out/data/thief.csv')
    df2 = pd.read_csv(f'out/data/r.csv')
    r = pd.merge(df2, df1, on=["run", "agentID"], how='outer')
    r.to_csv(f'out/data/merge.csv')
    pass



def perform_experiment():
    runs = 200
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
    print(f"change {hypothesis} given {evidence}: prior {H} to posterior {odds/(1+odds)} = {(odds/(1+odds)) - H}")
    return f"change {hypothesis} given {evidence}: prior {H} to posterior {odds/(1+odds)} = {(odds/(1+odds)) - H}"

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

def calculate_all_change(agent_type):
    df = pd.read_csv(f'out/data/{agent_type}.csv')
    dna = change(df, "DNAatCS", "suspect")
    statement = change(df, "statement", "locCS")
    df = pd.read_csv(f'out/data/r.csv') # given that the witness saw the victim
    witness = change(df, "other_cs", "other_suspect")
    alibi = change(df, "other_alib", "other_suspect")
    return dna, statement, witness, alibi

def calculate_all_change_merge(agent_type):
    df = pd.read_csv(f'out/data/merge.csv')
    dna = change(df, "DNAatCS", "suspect")
    statement = change(df, "statement", "locCS")
    witness = change(df, "other_cs", "other_suspect")
    alibi = change(df, "other_alib", "other_suspect")
    return dna, statement, witness, alibi

'''
Problem: how to transform the data in r.csv 
such that we get frequency distributions related to the stae space?
'''


l = []
for i in range(0, 1):
    #perform_experiment()
    #merge_attempt()

    #d, s, w, a = calculate_LRs("thief")
    #do, so, wo, ao = calculate_all_odds("thief")
    #do, so, wo, ao = calculate_all_change("thief")
    #do, so, wo, ao = calculate_all_change_merge("thief")

    l.append([calculate_all_change("thief"), calculate_all_change_merge("thief")])

#calculate_prior(f'out/data/thief.csv', "suspect")
#posterior(f'out/data/thief.csv', "DNAatCS", "suspect")

for lis in l:
    for do, so, wo, ao in lis:
        print(do)
        print(so)
        print(wo)
        print(ao)
        print()

    print()
    print()
    #print(f"LR DNA {d}, LR stat {s} LR witness {w}, LR alibi {a}")
    #print(f"odds DNA {do}, odds stat {so} odds witness {wo}, odds alibi {ao}")

os.system("Rscript generatingNetworkAlleys.R")

#calculate_LRs("thief")
#calculate_LRs("innocent")
