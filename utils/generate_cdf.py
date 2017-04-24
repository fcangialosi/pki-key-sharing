import pandas as pd
import numpy as np
import os

def generateCDF(file_path, cdf_path, weight=False, exclude_last = False):

    df = pd.read_csv(file_path, names=["cnt"])
    if(exclude_last):
        df = df[:-1]
    df['v'] = np.ones(len(df))
    cdf = df.groupby('cnt').sum()
    if(weight):
        cdf['v'] = cdf.index * cdf.v
    new_df =  cdf.cumsum()
    new_df = new_df.v / max(new_df.v)

    new_df.to_csv(cdf_path, sep="\t")#, header=False, index=False)

def generateCDFFromList(nums, cdf_path, weight=False, exclude_last = False):

    #df = pd.read_csv(file_path, names=["cnt"])
    df = pd.DataFrame({"cnt":nums})
    if(exclude_last):
        df = df[:-1]
    df['v'] = np.ones(len(df))
    cdf = df.groupby('cnt').sum()
    if(weight):
        cdf['v'] = cdf.index * cdf.v
    new_df =  cdf.cumsum()
    new_df = new_df.v / max(new_df.v)

    new_df.to_csv(cdf_path, sep="\t")#, header=False, index=False)

if __name__ == "__main__":
    a = [1,2,3,4,1,2,3,4,1,2,1,2,1,2]
    generateCDFFromList(a, "/tmp/tmp.tsv")
    sys.exit(1)
    RESULT_PATH = "/home/tjchung/research/luminati/dns/src/result/nxdomain"
    file_path = os.path.join(RESULT_PATH, "local_dns_content_ad.tsv")
    cdf_path = os.path.join(RESULT_PATH, "cdf/local_dns_content_ad.tsv")
    generateCDF(file_path, cdf_path)

    file_path = os.path.join(RESULT_PATH, "open_dns_content_ad.tsv")
    cdf_path  = os.path.join(RESULT_PATH, "cdf/open_dns_content_ad.tsv")

    file_path = os.path.join(RESULT_PATH, "theothers_dns_content_ad.tsv")
    file_path = os.path.join(RESULT_PATH, "theothers_dns_content_ad.tsv")

    file_path = os.path.join(RESULT_PATH, "local_dns_content_search.tsv")
    file_path = os.path.join(RESULT_PATH, "local_dns_content_search.tsv")

    file_path = os.path.join(RESULT_PATH, "open_dns_content_search.tsv")
    file_path = os.path.join(RESULT_PATH, "open_dns_content_search.tsv")

    file_path = os.path.join(RESULT_PATH, "theothers_dns_content_search.tsv")
    #file_path = "max_num_ips_invalid_certificate.tsv"
    #cdf_path = "cdf_max_num_ips_invalid_certificate.tsv"
    #generateCDF(file_path, cdf_path)
