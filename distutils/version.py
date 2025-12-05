from packaging.version import Version


class StrictVersion:
    """Minimal StrictVersion replacement powered by packaging.Version."""

    def __init__(self, version):
        if isinstance(version, StrictVersion):
            version = version.version
        self.version = Version(version)

    def __str__(self):
        return str(self.version)

    def __repr__(self):
        return f"StrictVersion({self.version})"

    def _compare(self, other):
        if not isinstance(other, StrictVersion):
            other = StrictVersion(other)
        return (self.version > other.version) - (self.version < other.version)

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def __eq__(self, other):
        return self._compare(other) == 0

    def __ne__(self, other):
        return self._compare(other) != 0


class LooseVersion(StrictVersion):
    """Lightweight LooseVersion equivalent that behaves like StrictVersion."""

    def __repr__(self):
        return f"LooseVersion({self.version})"

    def __str__(self):
        return str(self.version)


__all__ = ["StrictVersion", "LooseVersion"]
