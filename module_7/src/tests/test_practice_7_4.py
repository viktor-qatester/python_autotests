"""ПР №7.4: автоматизация тест-кейсов GitHub и Skillbox с помощью Playwright."""
import re

import allure
from playwright.sync_api import expect

from src.helpers import github, skillbox


@allure.suite("Поиск и фильтрация на GitHub и Skillbox")
class TestPractice74:
    @allure.title("Поиск задач GitHub: все заголовки issues содержат bug")
    def test_github_issues_search_by_title(self, page):
        github.open_issues(page)
        github.search_issues_in_title(page, "bug")

        titles = github.issue_titles(page)
        assert titles, "Не найдено ни одной задачи по фильтру in:title bug!"
        for title in titles:
            assert "bug" in title.lower(), f"Заголовок '{title}' не содержит слово 'bug'!"

    @allure.title("Фильтр Author: выбор bpasero применяется к поиску issues")
    def test_github_author_filter(self, page):
        author = "bpasero"
        github.open_issues(page)
        github.open_author_filter(page)

        assert author not in github.search_query_value(page), (
            f"Автор {author} уже присутствует в поиске до выбора!"
        )

        github.select_author(page, author)

        assert author in github.search_query_value(page) or author in page.url, (
            f"Фильтр по автору {author} не отображается в URL или строке поиска!"
        )

    @allure.title("Расширенный поиск: Python и репозитории со stars > 20000")
    def test_github_advanced_search(self, page):
        github.open_advanced_search(page)
        github.select_language_python(page)
        expect(page.locator(github.LANGUAGE_SELECT)).to_have_value("Python")

        github.fill_stars_filename_and_submit(page)

        star_counts = github.star_counts_from_results(page)
        assert star_counts, "Не удалось извлечь количество звёзд из результатов поиска!"
        assert all(count > 20000 for count in star_counts), (
            f"Есть репозитории с количеством звёзд <= 20000: {star_counts}"
        )

    @allure.title("Фильтры Skillbox: Профессия, 6–12 месяцев и тематика Docker")
    def test_skillbox_course_filters(self, page):
        skillbox.open_code_catalog(page)
        skillbox.close_cookie_banner(page)

        profession_tab = skillbox.select_profession(page)
        expect(profession_tab).to_have_class(re.compile("ui-tab--active"))

        skillbox.select_duration_6_12(page)
        skillbox.select_topic(page)
        expect(page).to_have_url(re.compile(f"topics={skillbox.SELECTED_TOPIC.lower()}"))

        url = page.url
        assert "type=profession" in url, f"В URL не отражён тип «Профессия»: {url}"
        assert "duration_min=6" in url and "duration_max=12" in url, (
            f"В URL не отражён диапазон длительности 6–12 месяцев: {url}"
        )

        cards = skillbox.wait_course_cards(page)
        assert cards.count() > 0, "После применения фильтров карточки не найдены!"

        cards_text = " ".join(cards.all_inner_texts())
        assert "профессия" in cards_text.lower(), "В карточках нет типа «Профессия»!"

        months = skillbox.months_from_text(cards_text)
        assert months, "В карточках не найдена длительность (N месяцев)!"
        assert all(6 <= month <= 12 for month in months), (
            f"Есть программы вне диапазона 6–12 мес.: {months}"
        )

    @allure.title("Тултип графика commit-activity показывает данные точки")
    def test_github_commit_activity_tooltip(self, page):
        github.open_commit_activity(page)
        point = github.chart_point(page)

        aria_label = point.get_attribute("aria-label") or ""
        commits_match = re.search(r"(\d+)\.\s*Commits", aria_label)
        assert commits_match, f"У точки графика нет ожидаемых данных в aria-label: {aria_label!r}"

        tooltip = github.chart_tooltip(page)
        expect(tooltip).to_be_hidden()

        github.hover_chart_point(point)
        expect(tooltip).to_be_visible()

        commits = commits_match.group(1)
        assert commits in github.tooltip_text(page), (
            f"Тултип не содержит ожидаемое количество коммитов: {commits}"
        )
