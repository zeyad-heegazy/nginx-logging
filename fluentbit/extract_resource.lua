-- Extract resource type and ID from request_uri
-- Lua uses its own pattern syntax (not PCRE): %d = digit, %- = literal hyphen
function extract_resource(tag, timestamp, record)
    local request_uri = record["request_uri"]

    -- Populate request_uri from request string if missing (json parser path)
    if not request_uri then
        local request = record["request"] or ""
        request_uri = string.match(request, "^%S+ (%S+)")
        if request_uri then
            record["request_uri"] = request_uri
        end
    end

    -- Populate request_method if missing
    if not record["request_method"] then
        local request = record["request"] or ""
        local method = string.match(request, "^(%S+)")
        if method then
            record["request_method"] = method
        end
    end

    if request_uri then
        -- Strip query string
        local path = string.match(request_uri, "^([^?]+)")

        local resource_type = nil
        local resource_id   = nil

        -- /api/admin/<resource>/<id>
        resource_type, resource_id = string.match(path, "^/api/admin/([a-z][a-z%-]*)/(%d+)")

        -- /api/admin/<resource>
        if not resource_type then
            resource_type = string.match(path, "^/api/admin/([a-z][a-z%-]*)")
        end

        -- /api/<resource>/<id>
        if not resource_type then
            resource_type, resource_id = string.match(path, "^/api/([a-z][a-z%-]*)/(%d+)")
        end

        -- /api/<resource>
        if not resource_type then
            resource_type = string.match(path, "^/api/([a-z][a-z%-]*)")
        end

        record["resource_type"] = resource_type
        record["resource_id"]   = resource_id and tonumber(resource_id) or nil
    end

    -- Remove fields no longer present in the ClickHouse schema
    record["request"]     = nil
    record["remote_user"] = nil

    return 2, timestamp, record
end
