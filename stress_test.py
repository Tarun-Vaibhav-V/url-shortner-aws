import requests, time, statistics, concurrent.futures

API_URL = 'https://tg9mlyqb01.execute-api.ap-south-1.amazonaws.com/prod'
SHORT_CODE = 'YfH7kE'  # https://github.com/Tarun-Vaibhav-V/url-shortener-aws
N_REQUESTS = 1000
CONCURRENCY = 8  # account Lambda concurrency limit is 10 on new accounts; stay under it


def one_request(_):
    start = time.perf_counter()
    r = requests.get(f'{API_URL}/{SHORT_CODE}', allow_redirects=False, timeout=10)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms, r.status_code


latencies = []
errors = 0

with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
    results = list(ex.map(one_request, range(N_REQUESTS)))

for lat, status in results:
    if status == 301:
        latencies.append(lat)
    else:
        errors += 1

latencies.sort()
print(f'Requests: {N_REQUESTS}  Errors: {errors}')
print(f'p50: {statistics.median(latencies):.1f}ms')
print(f'p95: {latencies[int(len(latencies)*0.95)]:.1f}ms')
print(f'p99: {latencies[int(len(latencies)*0.99)]:.1f}ms')
print(f'max: {max(latencies):.1f}ms')
