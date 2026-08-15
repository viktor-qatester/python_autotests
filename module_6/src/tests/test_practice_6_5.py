"""ПР №6.5: структура проекта, логирование, Allure-шаги, flake8."""
import allure
from selenium.webdriver.common.by import By

from src.helpers import github, skillbox


@allure.suite("Поиск и фильтрация на GitHub и Skillbox")
class TestPractice65:
    @allure.title("Поиск задач GitHub: все заголовки issues содержат bug")
    def test_github_issues_search_by_title(self, browser):
        github.open_issues(browser)
        assert "github.com" in browser.current_url, (
            f"GitHub не загрузился (возможный блок/сеть): {browser.current_url}"
        )
        github.search_issues_in_title_bug(browser)
        titles = github.issue_title_texts(browser)
        assert titles, "Не найдено ни одной задачи по фильтру in:title bug!"
        for title in titles:
            assert "bug" in title.lower(), (
                f"Заголовок '{title}' не содержит слово 'bug'!"
            )

    @allure.title("Фильтр Author: выбор bpasero меняет состояние поиска")
    def test_github_author_filter(self, browser):
        github.open_issues(browser)
        github.open_author_filter(browser)
        github.type_author(browser, "bpasero")

        value_before = github.search_query_value(browser)
        assert "bpasero" not in value_before, (
            "Автор bpasero уже присутствует в поиске до выбора!"
        )

        github.click_author_option(browser, "bpasero")
        github.wait_author_applied(browser, "bpasero")

        value_after = github.search_query_value(browser)
        current_url = browser.current_url
        assert "bpasero" in value_after or "bpasero" in current_url, (
            "Фильтр по автору bpasero не отображается в URL или строке поиска!"
        )

    @allure.title("Расширенный поиск: Python и репозитории со stars > 20000")
    def test_github_advanced_search(self, browser):
        github.open_advanced_search(browser)
        language_field = github.select_language_python(browser)
        selected_value = language_field.get_attribute("value")
        assert selected_value == "Python", (
            f"Поле языка не перешло в состояние 'Python', "
            f"текущее значение: {selected_value!r}"
        )
        github.fill_stars_filename_and_submit(browser)
        assert github.python_in_url(browser), (
            "Параметры поиска Python не найдены в URL!"
        )
        star_counts = github.star_counts_from_results(browser)
        assert star_counts, (
            "Не удалось извлечь количество звёзд из результатов поиска!"
        )
        assert all(count > 20000 for count in star_counts), (
            f"Есть репозитории с количеством звёзд <= 20000: {star_counts}"
        )

    @allure.title("Фильтры Skillbox: Профессия, 6–12 месяцев и тематика Docker")
    def test_skillbox_course_filters(self, browser):
        skillbox.open_code_catalog(browser)
        skillbox.close_cookie_banner(browser)
        skillbox.open_filters_modal(browser)

        profession_btn = skillbox.select_profession(browser)
        assert skillbox.is_profession_selected(profession_btn), (
            "Фильтр «Профессия» не применился после клика"
        )

        skillbox.select_duration_6_12(browser)
        skillbox.select_topic_docker(browser)
        skillbox.apply_filters(browser)

        cards = skillbox.wait_course_cards(browser)
        assert len(cards) > 0, "После применения фильтров карточки не найдены!"

        cards_text = skillbox.visible_cards_text(cards)
        page_text = browser.find_element(By.TAG_NAME, "body").text

        assert "профессия" in cards_text.lower(), (
            "В карточках нет типа 'Профессия'!"
        )

        months = skillbox.months_from_text(cards_text)
        assert months, "В карточках не найдена длительность (N месяцев)!"
        assert all(6 <= m <= 12 for m in months), (
            f"Есть программы вне диапазона 6–12 мес.: {months}"
        )

        assert skillbox.SELECTED_TOPIC.lower() in page_text.lower(), (
            f"Фильтр '{skillbox.SELECTED_TOPIC}' не отображается "
            f"на странице результатов!"
        )

    @allure.title("Тултип графика commit-activity появляется при наведении")
    def test_github_commit_activity_tooltip(self, browser):
        github.open_commit_activity(browser)
        chart_bar = github.chart_point(browser)

        expected_info = chart_bar.get_attribute("aria-label") or ""
        assert any(ch.isdigit() for ch in expected_info), (
            f"У точки графика нет ожидаемых данных в aria-label: "
            f"{expected_info!r}"
        )

        tooltip_before = github.tooltip_elements(browser)
        assert not tooltip_before, "Тултип отображается до наведения мыши!"

        github.hover_chart_point(browser, chart_bar)
        tooltip = github.wait_tooltip_visible(browser)
        assert tooltip.is_displayed(), "Tooltip не отображается при наведении!"
