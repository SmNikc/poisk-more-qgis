pythonimport pytest
from qgis.core import QgsHeatmapRenderer, QgsColorRampShader

@pytest.fixture
def heatmap_renderer():
    renderer = QgsHeatmapRenderer()
    color_ramp = QgsColorRampShader()
    color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
    renderer.setColorRamp(color_ramp)
    return renderer

def test_heatmap_renderer(heatmap_renderer):
    assert heatmap_renderer.type() == "heatmap"
    assert heatmap_renderer.radius() == 5  # Дефолт
    heatmap_renderer.setRadius(10)
    assert heatmap_renderer.radius() == 10