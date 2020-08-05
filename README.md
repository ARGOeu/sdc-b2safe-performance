
# sdc-b2safe-performance

This probe checks the basic data of b2safe (mem-free, swap-free)


`check_sdc_b2safe_performance.py --url <URL> --timeout <Timeout> -sf<Swap-free thresholds value> -mf<Mem-free threshold value> --verify`

`--url : Specify the url where the probe will exctract data from`

`--timeout : Timeout used for the requests to the service`

`-sf : Threshold declaration for the swap-free value, should be in the form of "{{warning-value}};{{critical-value}}", e.g. "400;600"`

`-mf : Threshold declaration for the mem-free value, should be in the form of "{{warning-value}};{{critical-value}}", e.g. "400;600"`

`--verify : Whether or not it should perform SSL verification on service`

### Example run

`./check_sdc_b2safe_performance.py --url https:b2safe.json --timeout 30 -sf "500;900" -mf "400;700"`