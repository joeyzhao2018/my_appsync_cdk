def nested_json_extractor(event, _context):
    # This is just an example, the actual structure of the event may vary
    # For this example, the trace context is located at event["request"]["headers"]
    nested_json = event.get("request", {}).get("headers", {})
    trace_id = nested_json.get("x-datadog-trace-id")
    parent_id = nested_json.get("x-datadog-parent-id")
    sampling_priority = nested_json.get("x-datadog-sampling-priority")

    # need to return the 3 values, i.e. trace_id, parent_id, sampling_priority
    return  trace_id, parent_id, sampling_priority
