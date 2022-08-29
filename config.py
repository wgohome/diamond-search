from pydantic import BaseSettings


class Settings(BaseSettings):
    PROTEIN_QUERIES_DIR: str = "queries/proteins"
    PROTEIN_QUERIES_SUFFIX: str = ".protein.query"
    PROTEIN_RESULTS_SUFFIX: str = ".diamond.out"
    PROTEIN_RESULTS_DIR: str = "results/proteins"

    def protein_query_filepath(self, job_id: str) -> str:
        return f"{self.PROTEIN_QUERIES_DIR}/{job_id}{self.PROTEIN_QUERIES_SUFFIX}"

    def protein_result_filepath(self, job_id: str) -> str:
        return f"{self.PROTEIN_RESULTS_DIR}/{job_id}{self.PROTEIN_RESULTS_SUFFIX}"

    def protein_query_job_id(self, filename: str | None = None, filepath: str | None = None) -> str:
        if filename is None and filepath is None:
            raise ValueError("Expects exactly one parameter of either filename or filepath")
        if filename and filepath:
            raise ValueError("Expects only one parameter of either filename or filepath")
        if filename:
            if "/" in filename:
                raise ValueError("Invalid filename, it should not be a path")
            return filename.rstrip(self.PROTEIN_QUERIES_SUFFIX)
        return filepath.rstrip(self.PROTEIN_QUERIES_SUFFIX).split("/")[-1]

    def protein_result_job_id(self, filename: str | None = None, filepath: str | None = None) -> str:
        if filename is None and filepath is None:
            raise ValueError("Expects exactly one parameter of either filename or filepath")
        if filename and filepath:
            raise ValueError("Expects only one parameter of either filename or filepath")
        if filename:
            if "/" in filename:
                raise ValueError("Invalid filename, it should not be a path")
            return filename.rstrip(self.PROTEIN_RESULTS_SUFFIX)
        return filepath.rstrip(self.PROTEIN_RESULTS_SUFFIX).split("/")[-1]


settings = Settings()

__all__ = ["settings"]
