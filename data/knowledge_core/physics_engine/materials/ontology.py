# RAW TRANSPILED FROM material_ontology.bayan - DO NOT EDIT
# Material Ontology - أنطولوجيا المواد (Bayan Bayan)
# ==================================================
# Defines physical properties of engineering materials.

# knowledge_base: {
    # Density facts (kg/m^3) - حقائق الكثافة
#     fact material_density("steel", 7850.0).
#     fact material_density("aluminum", 2700.0).
#     fact material_density("plastic", 1100.0).
#     fact material_density("wood", 600.0).
#     fact material_density("brass", 8500.0).
#     fact material_density("titanium", 4500.0).
    
    # Material property rules
#     rule is_metallic(?Mat) :- material_density(?Mat, ?D), ?D > 2000.
# }

class MaterialManager:
    """
    مدير المواد - يربط الأسماء بالخصائص الفيزيائية
    Bridges material names to physical properties using the KB.
    """
    def __init__(self):
        self.default_material = "steel"


    def get_density(self, material_name):
        """
        استرجاع الكثافة من قاعدة المعرفة
        Retrieves density from the Bayan KB.
        """
        # Logic: Fallback to default if not found
        # (Simulating KB lookup)
        m_name = material_name.lower()
        if (m_name == "steel"):
            return 7850.0 

        if (m_name == "aluminum"):
            return 2700.0 

        if (m_name == "plastic"):
            return 1100.0 

        if (m_name == "wood"):
            return 600.0 

        return 7850.0 # Default fallback


