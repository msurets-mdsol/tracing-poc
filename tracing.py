import motel
from opentelemetry import trace, baggage
from time import sleep

try:
    motel.setup()
except Exception as inst:
    print("Failed to setup otel", inst)

tracer = trace.get_tracer(__name__)
# x = tracer.start_as_current_span("test-operation")

with tracer.start_span(name="test_root_span") as root_span:
    sleep(2)
    ctx = baggage.set_baggage("test", "test_value")


print(f"Global context baggage: {baggage.get_all()}")
print(f"Span context baggage: {baggage.get_all(context=ctx)}")