from typing import TypedDict, List


class Result(TypedDict):
    dimension_values: List[str]
    value: int


class Breakdown(TypedDict, total=False):
    dimension_keys: List[str]
    results: List[Result]  

class TotalValue(TypedDict, total=False):
    value: int
    breakdowns: List[Breakdown]


class MetricItem(TypedDict):
    name: str
    period: str
    title: str
    description: str
    total_value: TotalValue
    id: str


class PagingInfo(TypedDict):
    previous: str
    next: str

class SimpleTotalValue(TypedDict):
    value: int

class SimpleInsightEntry(TypedDict):
    name: str
    period: str
    title: str
    description: str
    total_value: SimpleTotalValue
    id: str

class TotalValueWithBreakdownOnly(TypedDict):
    breakdowns: List[Breakdown]

class InsightEntryWithBreakdownOnly(TypedDict):
    name: str
    period: str
    title: str
    description: str
    total_value: TotalValueWithBreakdownOnly
    id: str


class InsightsResponse(TypedDict):
    data: List[MetricItem]
    paging: PagingInfo

class SimpleInsightsResponse(TypedDict):
    data: List[SimpleInsightEntry]
    paging: PagingInfo

class FollowsAndUnfollowsResponse(TypedDict):
    data: List[InsightEntryWithBreakdownOnly]
    paging: PagingInfo