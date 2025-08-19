from qgis.core import QgsMapSettings, QgsMapRendererJob
class ExportMapAsRaster:
    def execute(self, output_path: str):
        settings = QgsMapSettings()
        job = QgsMapRendererJob(settings)
        job.start()
        job.waitForFinished()