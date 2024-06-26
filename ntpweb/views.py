import logging
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
import ntplib
import socket
import time
import json

# Configure logging
logger = logging.getLogger(__name__)

def csrf_token_view(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

def get_offset_and_delay_from_otherntp(server):
    ntp_client = ntplib.NTPClient()
    try:
        response = ntp_client.request(server, timeout=10)  # Increased timeout to 10 seconds
        offset = response.offset
        delay = response.delay
        processing_time = response.tx_time - response.recv_time
        return offset, delay, processing_time, response
    except (ntplib.NTPException, socket.timeout) as e:
        logger.error(f"Error querying NTP server {server}: {e}")
        return None, None, None, None

def generate_graphs():
    other_ntp_servers = [
        'time.nplindia.org', 'time.nplindia.in',
        '14.139.60.103', '14.139.60.106', '14.139.60.107',
        'samay1.nic.in', 'samay2.nic.in', '157.20.66.8', '157.20.67.8',
        'time.nist.gov', 'time.google.com', 'uk.pool.ntp.org', 'time.windows.com',
        'ptbtime1.ptb.de',
    ]

    other_server_names = []
    offsets2 = []
    delays2 = []
    processing_time2 = []

    for server2 in other_ntp_servers:
        offset, delay, processing_time, response = get_offset_and_delay_from_otherntp(server2)
        other_server_names.append(server2)
        if response:
            offsets2.append(offset)
            delays2.append(delay)
            processing_time2.append(processing_time)
        else:
            offsets2.append(0)  # Use 0 or a placeholder value
            delays2.append(0)   # Use 0 or a placeholder value
            processing_time2.append(0)  # Use 0 or a placeholder value
            logger.warning(f"No response from NTP server {server2}")

    return {
        'servers': other_server_names,
        'offsets': offsets2,
        'delays': delays2,
        'processing_times': processing_time2
    }

def ntp_data(request):
    return render(request, 'ntpweb/index.html')

def dynamic_graph(request):
    data = generate_graphs()
    return JsonResponse(data)

@method_decorator(csrf_exempt, name='dispatch')
class SearchView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            search_input = data.get('search_input')
            csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
            logger.info(f"Received search input: {search_input}")
            logger.info(f"CSRF Token: {csrf_token}")
            logger.info("Request Headers: %s", request.headers)

            if search_input:
                offset, delay, processing_time, response = get_offset_and_delay_from_otherntp(search_input)
                if response:
                    packet_details = {
                        "Leap indicator": response.leap,
                        "Version": response.version,
                        "Mode": response.mode,
                        "Stratum": response.stratum,
                        "Poll": response.poll,
                        "Precision": response.precision,
                        "Root delay": response.root_delay,
                        "Root dispersion": response.root_dispersion,
                        "Reference ID": response.ref_id,
                        "Reference time": response.ref_time,
                        "Readable reference time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response.ref_time)),
                        "Originate time": response.orig_time,
                        "Readable T1 timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response.orig_time)),
                        "Receive time": response.recv_time,
                        "Readable T2 timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response.recv_time)),
                        "Transmit time": response.tx_time,
                        "Readable T3 timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response.tx_time)),
                        "Server processing time": processing_time
                    }
                    return JsonResponse(packet_details)
                else:
                    logger.error("No response received from NTP server.")
                    return JsonResponse({"error": "No response received from NTP server."}, status=500)
            else:
                logger.error("Search input parameter 'search_input' is missing.")
                return JsonResponse({"error": "Search input parameter 'search_input' is missing."}, status=400)
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            return JsonResponse({"error": "Internal Server Error"}, status=500)

    def get(self, request, *args, kwargs):
        csrf_token = get_token(request)
        return JsonResponse({"csrf_token": csrf_token})

def get_ntp_time(request):
    ntp_servers = [
        'time.google.com',
        'time.nist.gov',
        'pool.ntp.org',
        'time.windows.com',
        'samay1.nic.in',
        'samay2.nic.in',
        'time.nplindia.org', 
        'time.nplindia.in',
    ]

    client = ntplib.NTPClient()
    for server in ntp_servers:
        try:
            response = client.request(server, timeout=5)
            ntp_time = response.tx_time
            return JsonResponse({'ntp_time': ntp_time})
        except (ntplib.NTPException, socket.timeout) as e:
            logger.error(f"Error querying NTP server {server}: {e}")

    return JsonResponse({'error': 'All NTP servers failed to respond'}, status=500)
