
class Mdl_Search:
    """Get matched metric metadata, like metric definition and referenced datasource with table schema"""
    def __init__(self):
        self.name = "metric metadata search"
        self.description = "Get matched metric metadata, like metric definition and referenced datasource with table schema."

    def run(self, question: str) -> list[str]:
        ret =[]

        task_path = 'semantic/modeling_definition_language/user_order.yml'
        with open(task_path, "r") as f:
            ret.append(f.read().strip())
        
        return ret