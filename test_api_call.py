import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# New test input
input_text = """
Multi-link Operation
Multi-link operation (a.k.a MLO) – enables aggregation of multiple bands or channels. With MLO, the Wi-Fi 7 Access Point and Client devices can associate and simultaneously exchange traffic on multiple bands (or multiple channels in the same band if the access point has a dual 5 GHz radio). The distribution of traffic on different bands helps achieve higher throughput, reduced latency and improves reliability. This is a mandatory feature for Wi-Fi 7 certification.

Main benefits of MLO:

Aggregation: The AP and client can now use multiple links to exchange data. This will help in increased throughput and benefits applications like high definition video conferencing.

Steering: Multi link is also aiming to dynamically steer the clients to exchange data in the link, where it can achieve better SLA for certain traffic flows. If there is an application requiring strict SLA, it can dynamically switch the links, based on the channel conditions that the AP and clients think that it can achieve the SLA. An example here would be the AR/VR applications.

Redundancy: The access point and the clients can send the same data on multiple links. If there is a packet drop in one of the links due to corruption, the duplicate data on the other link can be used. This helps to improve the reliability. An example application here would be remote surgery where the application cannot afford any data drops due to the critical nature of the application.

In the initial phase, the main benefit that the end users will achieve is the higher throughput with the aggregation functionality.

The devices that are capable of performing multi-link operations are called Multi-Link Devices or MLD. The access points are referred to as AP MLD and clients are referred to as Non-AP MLD.
"""

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Please reword the following text in a more interesting and less technical way: {input_text}"}
        ]
    )
    reworded_text = response['choices'][0]['message']['content']
    print("Reworded Text:", reworded_text)
except Exception as e:
    print("Error during OpenAI API call:", str(e))
