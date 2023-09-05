# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %%
import pathmagic

# %%
with pathmagic.context():
    from func.logme import log
    from func.gmailfetch import getworknewmail

# %%
if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # fetchworkfile_from_gmail('')
    getworknewmail()
    log.info(f'文件{__file__}运行结束！')
