vegeta attack -rate=21 -duration=10s -targets=target_onion.txt -body=sample_cheese_body.txt > output.bin
vegeta attack -rate=2 -duration=1s -targets=target_onion.txt -body=sample_milk_body.txt > output.bin
vegeta attack -rate=19 -duration=10s -targets=target_onion.txt -body=sample_cheese_body.txt > output.bin
vegeta attack -rate=2 -duration=5s -targets=target_onion.txt -body=sample_almonds_body.txt > output.bin
vegeta attack -rate=10 -duration=10s -targets=target_onion.txt -body=sample_cheese_body.txt > output.bin
echo "Produces 4980 log messages"

