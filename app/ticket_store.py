from uuid import uuid4

from app.models import (
    DraftStatus,
    JiraTicket,
    TicketDraft,
    TicketUpdateRequest,
)


class TicketStore:
    def __init__(self):
        self.drafts: dict[str, TicketDraft] = {}

    def create_draft(
        self,
        ticket: JiraTicket
    ) -> TicketDraft:
        draft_id = str(uuid4())

        draft = TicketDraft(
            draft_id=draft_id,
            status=DraftStatus.DRAFT,
            ticket=ticket
        )

        self.drafts[draft_id] = draft

        return draft

    def get_draft(
        self,
        draft_id: str
    ) -> TicketDraft | None:
        return self.drafts.get(draft_id)

    def update_draft(
        self,
        draft_id: str,
        updates: TicketUpdateRequest
    ) -> TicketDraft | None:
        draft = self.get_draft(draft_id)

        if draft is None:
            return None

        if draft.status != DraftStatus.DRAFT:
            raise ValueError(
                "Only drafts with DRAFT status can be edited"
            )

        update_data = updates.model_dump(
            exclude_unset=True
        )

        updated_ticket_data = (
            draft.ticket.model_dump()
        )

        updated_ticket_data.update(
            update_data
        )

        draft.ticket = JiraTicket(
            **updated_ticket_data
        )

        self.drafts[draft_id] = draft

        return draft

    def approve_draft(
        self,
        draft_id: str
    ) -> TicketDraft | None:
        draft = self.get_draft(draft_id)

        if draft is None:
            return None

        if draft.status != DraftStatus.DRAFT:
            raise ValueError(
                "Only drafts with DRAFT status can be approved"
            )

        draft.status = DraftStatus.APPROVED

        self.drafts[draft_id] = draft

        return draft

    def reject_draft(
        self,
        draft_id: str
    ) -> TicketDraft | None:
        draft = self.get_draft(draft_id)

        if draft is None:
            return None

        if draft.status != DraftStatus.DRAFT:
            raise ValueError(
                "Only drafts with DRAFT status can be rejected"
            )

        draft.status = DraftStatus.REJECTED

        self.drafts[draft_id] = draft

        return draft

    def mark_created(
        self,
        draft_id: str,
        jira_key: str,
        jira_url: str
    ) -> TicketDraft | None:
        draft = self.get_draft(draft_id)

        if draft is None:
            return None

        if draft.status != DraftStatus.APPROVED:
            raise ValueError(
                "Only approved drafts can be marked as CREATED"
            )

        draft.status = DraftStatus.CREATED
        draft.jira_key = jira_key
        draft.jira_url = jira_url

        self.drafts[draft_id] = draft

        return draft


ticket_store = TicketStore()
