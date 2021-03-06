import zeeguu_core
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from zeeguu_core.model.cohort import Cohort
from zeeguu_core.model.article import Article


class CohortArticleMap(zeeguu_core.db.Model):

    cohort_id = Column(Integer, ForeignKey(Cohort.id))
    cohort = relationship(Cohort)

    article_id = Column(Integer, ForeignKey(Article.id))
    article = relationship(Article)
    __table_args__ = (
        PrimaryKeyConstraint(cohort_id, article_id),
        {"mysql_collate": "utf8_bin"},
    )

    def __init__(self, cohort, article):
        self.cohort = cohort
        self.article = article

    @classmethod
    def find(cls, cohort_id, article_id):
        return cls.query.filter_by(article_id=article_id, cohort_id=cohort_id).first()

    @classmethod
    def get_articles_info_for_cohort(cls, cohort):
        articles = [
            relation.article.article_info()
            for relation in cls.query.filter_by(cohort=cohort).all()
        ]
        return sorted(articles, key=lambda x: x["metrics"]["difficulty"])

    @classmethod
    def get_cohorts_for_article(cls, article):
        cohorts = [
            cohort_article_entry.cohort.name
            for cohort_article_entry in cls.query.filter_by(article=article).all()
        ]
        return cohorts
