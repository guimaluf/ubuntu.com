import dateutil.parser
from marshmallow import Schema
from marshmallow.fields import (
    Boolean,
    DateTime,
    Dict,
    Float,
    List,
    Nested,
    String,
)
from marshmallow.validate import Regexp


# Types
# ===


class ParsedDateTime(DateTime):
    default_error_messages = {"parse_error": "dateutil cannot parse {input}."}

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            date = dateutil.parser.parse(value)
        except (OverflowError, ValueError):
            raise self.make_error("parse_error", input=value)

        return super()._deserialize(date.isoformat(), attr, data, **kwargs)


class ReleaseCodename(String):
    default_error_messages = {
        "unrecognised_codename": "Cannot find a release with codename {input}"
    }

    def _deserialize(self, value, attr, data, **kwargs):
        if value not in self.context["release_codenames"]:
            raise self.make_error("unrecognised_codename", input=value)

        return super()._deserialize(value, attr, data, **kwargs)


# Schemas
# ===


# Notices
# --
class NoticePackage(Schema):
    name = String(required=True)
    version = String(required=True)
    description = String()
    is_source = Boolean(required=True)
    source_link = String(allow_none=True)
    version_link = String(allow_none=True)


class NoticeSchema(Schema):
    id = String(required=True, validate=Regexp(r"USN-\d{4}-\d{1,2}"))
    title = String(required=True)
    summary = String(required=True)
    instructions = String(required=True)
    references = List(String())
    cves = List(String(validate=Regexp(r"(cve-|CVE-)\d{4}-\d{4,7}")))
    published = ParsedDateTime(required=True)
    description = String(allow_none=True)
    release_packages = Dict(
        keys=ReleaseCodename(),
        values=List(Nested(NoticePackage), required=True),
    )


# CVEs
# --
class Status(Schema):
    release_codename = ReleaseCodename(required=True)
    status = String(required=True)
    description = String(allow_none=True)


class CvePackage(Schema):
    name = String(required=True)
    source = String(required=True)
    ubuntu = String(required=True)
    debian = String(required=True)
    statuses = List(Nested(Status))


class Note(Schema):
    author = String(required=True)
    note = String(required=True)


class CVESchema(Schema):
    id = String(required=True)
    published = ParsedDateTime(allow_none=True)
    description = String(allow_none=True)
    ubuntu_description = String(allow_none=True)
    notes = List(Nested(Note))
    priority = String(allow_none=True)
    status = String(allow_none=True)
    cvss3 = Float(allow_none=True)
    packages = List(Nested(CvePackage))
    references = List(String())
    bugs = List(String())
