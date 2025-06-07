from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(_BaseModel):
    """全体共通の情報をセットするBaseSchema"""

    model_config = ConfigDict(
        from_attributes=True,  # 辞書ではなく .属性 で持っているデータを直接パース可能にする
        alias_generator=to_camel,  # jsonのキーをキャメルケースに変換
        populate_by_name=True,  # スネークケースでも値を受け付ける
        strict=True
    )
