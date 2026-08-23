"""The calculator workflow must behave exactly as before the re-theme."""

import pytest

from main import compute


class TestCompute:
    @pytest.mark.parametrize(
        ("a", "b", "op", "expected"),
        [
            (2, 3, "add", 5),
            (-2.5, 0.5, "add", -2.0),
            (10, 4, "sub", 6),
            (3, 7, "sub", -4),
            (6, 7, "mul", 42),
            (2.5, 4, "mul", 10.0),
            (9, 3, "div", 3),
            (7, 2, "div", 3.5),
        ],
    )
    def test_operations(self, a, b, op, expected):
        assert compute(a, b, op) == pytest.approx(expected)

    def test_divide_by_zero_raises(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            compute(1, 0, "div")

    def test_unknown_operation_raises(self):
        with pytest.raises(ValueError, match="Unknown operation: pow"):
            compute(2, 3, "pow")


class TestRoutes:
    def test_get_renders_empty_form(self, client):
        response = client.get("/")
        assert response.status_code == 200
        body = response.text
        assert 'class="calculator"' in body
        assert 'class="result"' not in body
        assert 'class="error"' not in body

    def test_get_offers_every_operation(self, client):
        body = client.get("/").text
        for op in ("add", "sub", "mul", "div"):
            assert f'value="{op}"' in body

    def test_post_renders_result(self, client):
        response = client.post("/", data={"a": "8", "b": "5", "op": "add"})
        assert response.status_code == 200
        assert 'class="result"' in response.text
        assert "13" in response.text
        assert 'class="error"' not in response.text

    def test_post_divide_by_zero_renders_error(self, client):
        response = client.post("/", data={"a": "8", "b": "0", "op": "div"})
        assert response.status_code == 200
        assert 'class="error"' in response.text
        assert "Cannot divide by zero" in response.text
        assert 'class="result"' not in response.text

    def test_post_keeps_selected_operation(self, client):
        body = client.post("/", data={"a": "8", "b": "2", "op": "mul"}).text
        assert '<option value="mul" selected>' in body

    def test_post_rejects_non_numeric_input(self, client):
        response = client.post("/", data={"a": "abc", "b": "2", "op": "add"})
        assert response.status_code == 422

    def test_stylesheet_is_served(self, client):
        response = client.get("/static/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
