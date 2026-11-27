import dataclasses
import enum

PROJECT_ID = "19684"  # Data Ecosystem & AI: Finance  (DEFIN)
TEAM_ID = "6933e7bd-dfcc-4128-85e3-1031949546a0"  # DEFIN_KIWI


@dataclasses.dataclass
class LabelledID:
    id: str
    label: str


class LabelledEnum(enum.Enum):
    value: LabelledID

    @property
    def id(self) -> str:
        return self.value.id

    @property
    def label(self) -> str:
        return self.value.label


class IssueType(LabelledEnum):
    EPIC = LabelledID(id="10000", label="Epic")
    STORY = LabelledID(id="10023", label="Story")
    TASK = LabelledID(id="10021", label="Task")
    BUG = LabelledID(id="10024", label="Bug")
    # SUBTASK = LabelledID(id="10022", label="Sub-task")


class Priority(LabelledEnum):
    LOW = LabelledID(id="10010", label="Low")
    MEDIUM = LabelledID(id="10009", label="Medium")
    HIGH = LabelledID(id="10008", label="High")
    VERY_HIGH = LabelledID(id="10016", label="Very High")


class Label(enum.StrEnum):
    MANAGEMENT = "KiwiManagement"
    MODELLING = "KiwiDataModelling"
    ENGINEERING = "KiwiEngineering"
    ORANGE = "OrangeKiwi"
    RED = "RedKiwi"


@dataclasses.dataclass
class CreatePayload:
    summary: str

    assignee: str | None = dataclasses.field(default=None)
    description: str | None = dataclasses.field(default=None)
    issue_type: IssueType = dataclasses.field(default=IssueType.TASK)
    labels: list[Label] | None = dataclasses.field(default=None)
    parent: None = dataclasses.field(default=None)
    priority: Priority | None = dataclasses.field(default=None)
    project: str = dataclasses.field(default=PROJECT_ID)
    team: str = dataclasses.field(default=TEAM_ID)

    def to_payload(self) -> dict:
        assignee = {} if self.assignee is None else {
            "assignee": {"id": self.assignee},
        }
        description = {} if self.description is None else {
            "description": {
              "content": [
                {
                  "content": [
                    {
                      "text": self.description,
                      "type": "text"
                    }
                  ],
                  "type": "paragraph"
                }
              ],
              "type": "doc",
              "version": 1
            },
        }
        issue_type = {"issuetype": {"id": self.issue_type.id}}
        labels = {} if self.labels is None else {"labels": self.labels}
        parent = {} if self.parent is None else {"parent": {"key": self.parent}}  # TODO: Enforce that `self.parent` is a key, not ID or nme
        priority = {} if self.priority is None else {
            "priority": {"id": self.priority.id},
        }
        project = {"project": {"id": self.project}}
        summary = {} if self.summary is None else {"summary": self.summary}
        team = {"customfield_10001": self.team}

        return {
            "fields": (
                {}
                | assignee
                | description
                | issue_type
                | labels
                | parent
                | priority
                | project
                | summary
                | team
            )
        }
