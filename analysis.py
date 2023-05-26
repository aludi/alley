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


def transform_ret(ret): # at least 1 other agent says about them that they were at CS/had alibi.
    ag_list = []
    run_num = 0

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

        print(run_num)
        for i in d_cs.keys():
            print(f"{i} was seen by {d_cs[i]} agents at crime scene")
            print(f"{i} was seen by {d_al[i]} agents away from crime scene")
            if d_cs[i] > 0:
                cs_witness = 1
            else:
                cs_witness = 0
            if d_al[i] > 1:
                alibi_witness = 1
            else:
                alibi_witness = 0

            ag_list.append([run_num, i, cs_witness, alibi_witness])

    print(ag_list)

    df = pd.DataFrame(ag_list, columns=["run", "agentID", "at_least_1_cs_witness", "at_least_1_alibi_witness"])
    df.to_csv(f'out/data/witness.csv')


    #exit()


def export_ret(r):
    df_list = []
    for x in r:
        d = pd.DataFrame(x, columns= ["run", "agentID", "other", "other_thief", "other_suspect", "other_cs", "other_alib"])
        df_list.append(d)
    df = pd.concat(df_list)
    df.to_csv(f'out/data/r.csv')

def merge_attempt():
    df1 = pd.read_csv(f'out/data/thief.csv')
    df2 = pd.read_csv(f'out/data/witness.csv')
    r = pd.merge(df1, df2, on=["run", "agentID"], how='outer')
    r.to_csv(f'out/data/merge.csv')
    pass


def perform_experiment():
    runs = 100
    for i in range(0, 1):
        e = Experiment(run=runs, suspect="thief")
        params = {"experiment_name": "thief", "runs":runs}
        export_to_df(e,params)
        export_ret(e.r)
        transform_ret(e.r)
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
    l = [("DNAatCS", "suspect"), ("statement", "locCS"),
         ("at_least_1_cs_witness", "suspect"), ("at_least_1_alibi_witness", "suspect")]

    for (ev, hyp) in l:
        change(df,ev, hyp)
    print("end")
    dna = change(df, "DNAatCS", "suspect")
    statement = change(df, "statement", "locCS")
    witness = change(df, "at_least_1_cs_witness", "suspect")
    alibi = change(df, "at_least_1_alibi_witness", "suspect")
    return dna, statement, witness, alibi

'''
Problem: how to transform the data in r.csv 
such that we get frequency distributions related to the stae space?
'''


l = []
for i in range(0, 1):
    perform_experiment()
    merge_attempt()

    #d, s, w, a = calculate_LRs("thief")
    #do, so, wo, ao = calculate_all_odds("thief")
    #do, so, wo, ao = calculate_all_change("thief")
    #do, so, wo, ao = calculate_all_change_merge("thief")

    l.append([calculate_all_change_merge("thief")])

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

