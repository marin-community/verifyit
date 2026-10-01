FROM python@sha256:e41613d42d4891e4930f79523f93f81bbc7632584ec65e36ab055f41a800b41e
RUN pip install --no-cache-dir sympy==1.14.0 mpmath==1.3.0 regex==2026.7.10 loguru==0.7.3 antlr4-python3-runtime==4.11.0
COPY matharena /opt/matharena
COPY verifyit_hmmt_values.py /opt/verifyit_hmmt_values.py
RUN python -c 'import shutil, sysconfig; p=sysconfig.get_paths()["purelib"]; shutil.copytree("/opt/matharena",p+"/matharena"); shutil.copy("/opt/verifyit_hmmt_values.py",p+"/verifyit_hmmt_values.py")'
