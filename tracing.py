import motel
from opentelemetry import trace
from time import sleep

try:
    motel.setup()
except Exception as inst:
    print("Failed to setup otel", inst)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(name="test_root_span") as root_span:
    sleep(0.5)
    with tracer.start_as_current_span("test-operation"):
        # Call other services
        sleep(2)
    sleep(0.5)
