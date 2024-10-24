from FERS_core.members.memberset import MemberSet


class TranslationImperfection:
    def __init__(
        self,
        memberset: list[MemberSet],
        magnitude: float,
        axis: tuple,
    ):
        """
        Initialize a translation imperfection applied to a member.

        Args:
            member: The member to which the imperfection is applied.
            load_case: The LoadCase instance this imperfection is associated with.
            magnitude (float): The magnitude of the translation.
            direction (tuple): The direction of the translation (e.g., (1, 0, 0) for X-axis).
        """
        self.member = memberset
        self.magnitude = magnitude
        self.axis = axis