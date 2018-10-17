# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, INTEGER, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.ext.declarative import declarative_base

# Code generated using:
# sqlacodegen mysql+pymysql://<username>:<password>@localhost:3306/pgd_r_17_1 --outfile pgd_r_17_1.py

Base = declarative_base()
metadata = Base.metadata

### NOTE: Refer to this GitHub issue re: tables with field called relationship interferes with the relationship function:
# https://github.com / agronholm / sqlacodegen / issues / 68

class Aro(Base):
    __tablename__ = 'aro'
    id = Column(INTEGER, primary_key=True)
    accession = Column(String(10))
    cvterm_id = Column(INTEGER, nullable=False)
    term = Column(String(255))
    namespace = Column(String(25))
    xref = Column(String(50))
    definition = Column(Text)
    version = Column(String(25))

class GenomeProjectCoreProject(Base):
    __tablename__ = 'genome_project_core_project'

    id = Column(INTEGER, primary_key=True)
    curated = Column(INTEGER, nullable=False)
    project_title = Column(Text)
    project_db = Column(String(25))
    project_accession = Column(String(50))
    project_description= Column(Text)
    organism_name = Column(Text)
    publication_citation = Column(String(250))
    sample_provider_pi_institution = Column(String(250))
    sample_provider_pi_email = Column(String(250))
    linked_project_id = Column(INTEGER, nullable=True)
    num_samples = Column(INTEGER, nullable=False)
    release_date = Column(String(10))

class GenomeProjectCoreSample(Base):
    __tablename__ = 'genome_project_core_sample'
    id = Column(INTEGER, primary_key=True)
    curated = Column(INTEGER, nullable=False)
    sample_title = Column(Text)
    sample_name = Column(String(250))
    sample_db = Column(String(25))
    sample_accession = Column(String(20))


class GenomeProjectSequenceAssembly(Base):
    __tablename__ = 'genome_project_sequence_assembly'

    id = Column(INTEGER, primary_key=True)
    sample_id = Column(INTEGER)
    assembly_db = Column(String(25))
    assembly_accession = Column(String(250))
    assembly_name = Column(String(250))
    release_date = Column(String(25))
    assembly_status = Column(String(25))
    scaffolds_count = Column(INTEGER)
    scaffold_n50 = Column(INTEGER)
    scaffold_n90 = Column(INTEGER)
    contig_count = Column(INTEGER)
    contig_n50 = Column(INTEGER)
    contig_n90 = Column(INTEGER)
    assembly_total_length = Column(INTEGER)
    ftp_path = Column(String(255))


class Strain(Base):
    __tablename__ = 'strain'
    strain_id = Column(INTEGER, primary_key=True)
    species = Column(String(255))
    strain = Column(String(45))
    percent_gc = Column(String(10))

    genes = Column(INTEGER)
    availability = Column(Enum('public', 'private'))
    user_id = Column(INTEGER)

    organism = Column(String(255))
    assembly_level = Column(String(255))
    analysis_folder = Column(String(255))

    priority = Column(INTEGER)
    annotations_loaded = Column(INTEGER)
    genome_project_sequence_assembly_id = Column(INTEGER)


class StrainAntibioticSusceptibility(Base):
    __tablename__ = 'strain_antibiotic_susceptibility'
    id = Column(INTEGER, primary_key=True)
    strain_id = Column(INTEGER)
    antibiotic = Column(String(250))
    aro_term = Column(String(20))
    phenotype = Column(Enum('resistant','susceptible','not defined','undefined','intermediate','nonsusceptible','susceptible-dose dependent'))
    pmid = Column(INTEGER)
    measurement_sign = Column(Enum('<','<=','==','>','>='))
    measurement = Column(String(10))
    measurement_units = Column(Enum('mg/L','mm'))
    laboratory_typing_method = Column(Enum('MIC','agar dilution','disk diffusion'))
    laboratory_typing_platform = Column(Enum('Microscan','Phoenix','Sensititre','Vitek'))
    vendor = Column(Enum('Becton Dickinson','Biomérieux','Siemens','Trek','Biom?rieux','Biomerieux'))
    laboratory_typing_method_version_or_reagent = Column(Enum('96-Well Plate','E-Test','GM-NEG'))
    testing_standard= Column(Enum('BSAC','CLSI','DIN','EUCAST','NARMS','NCCLS','SFM','SIR','WRG'))
