import time
from opentelemetry import trace, baggage, context
from opentelemetry.context import attach
import motel


try:
    motel.setup()
except Exception as inst:
    print("Failed to setup otel", inst)

tracer = trace.get_tracer(__name__)


def service_a():
    # Start a trace (root span)
    with tracer.start_as_current_span("ServiceA.Operation") as span_a:
        print(f"[Service A] Span ID: {span_a.get_span_context().span_id}")
        print(f"[Service A] Current Baggage: {baggage.get_all()}")

        # === SET BAGGAGE ===
        # Baggage is stored in the current Context
        # Create a new context containing the baggage item
        ctx = baggage.set_baggage("userID", "user-123")
        ctx = baggage.set_baggage("userTier", "premium", context=ctx)

        print("[Service A] Setting Baggage: userID=user-123, userTier=premium")

        # Attach the context with baggage so it becomes current
        # for downstream calls (or use context.with_current() context manager)

        attach(ctx)
        try:
            service_b()  # Call next service
        finally:
            pass  # detach(token) - implicit context usually handles this


def service_b():
    with tracer.start_as_current_span("ServiceB.Processing") as span_b:
        print(f"[Service B] Span ID: {span_b.get_span_context().span_id}")

        # === READ BAGGAGE ===
        user_id = baggage.get_baggage("userID")
        user_tier = baggage.get_baggage("userTier")
        non_existent = baggage.get_baggage("otherKey")  # Returns None if not found

        print(
            f"[Service B] Read Baggage: userID={user_id}, userTier={user_tier}, otherKey={non_existent}"
        )

        # === Optionally add Baggage as Span Attribute ===
        # Check if baggage exists before adding as attribute
        if user_id:
            span_b.set_attribute("app.user.id", user_id)
            print("[Service B] Added 'app.user.id' attribute to current span.")
        if user_tier:
            span_b.set_attribute("app.user.tier", user_tier)
            print("[Service B] Added 'app.user.tier' attribute to current span.")

        # Simulate work
        time.sleep(0.1)
        service_c()  # Call next service


def service_c():
    with tracer.start_as_current_span("ServiceC.FinalStep") as span_c:
        print(f"[Service C] Span ID: {span_c.get_span_context().span_id}")
        # Can still read baggage here
        user_id = baggage.get_baggage("userID")
        print(f"[Service C] Read Baggage: userID={user_id}")
        # Add as attribute if needed for this span's context
        if user_id:
            span_c.set_attribute("app.user.id", user_id)


# --- Run the example ---
print("Starting trace...")
service_a()
print("Trace finished.")
