# get-logs
Script para capturar e salvar trechos de logs já existentes baseados na data e no horário desejado.

Exemplo de uso:

```
$ python get-logs.py --help

usage: get-logs.py [-h] [-d DATE_RANGE] [-t TIME_RANGE] [-p LOG_PREFIX]
                     [--log-dir LOG_DIR] [-o OUTPUT_NAME]

Get all logs

optional arguments:
  -h, --help         show this help message and exit
  -d DATE_RANGE      Set the date range from the begining to the end separated
                     by commas (,). Example: 01-01-2010,31-12-2015
  -t TIME_RANGE      Set the time range from the begining to the end separated
                     by commas (,). Example: 00:00:00,23:59:59
  -p LOG_PREFIX      Get logs based on its name prefix separated by commas
                     (,). Example: powerMonitor,suiteCore,network
  --log-dir LOG_DIR  Absolute path to the log directory
  -o OUTPUT_NAME     Output TAR filename.
  
$ python get-logs.py -p powerMonitorInfo.log -d '2016-01-25,2016-01-26'`
```



