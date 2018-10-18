# /usr/bin/python3

import os
import time
import re
import sys
from pgd_schema import Aro, Strain, StrainAntibioticSusceptibility, GenomeProjectCoreSample,GenomeProjectSequenceAssembly
from optparse import OptionParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def main():
    # Get options from the command line
    parser = OptionParser()
    parser.add_option("--organism", dest="organism", action="store", type="string", help="Genus, species or strain name",metavar="ORGANISM")
    parser.add_option("--assembly", action="store_true", dest="assembly")
    parser.add_option("--sra", action="store_true", dest="sra")
    parser.add_option("--out", dest="out", action="store", type="string", help="Output path and file name",metavar="OUT", default="out.txt")

    parser.add_option("-d", "--database", dest="database", action="store", type="string",help="Name of database you wish to connect to", metavar="DATABASE")
    parser.add_option("-H", "--host", dest="host", action="store", type="string", help="Database host", metavar="HOST")
    parser.add_option("-u", "--user", dest="user", action="store", type="string", help="User name", metavar="NAME")
    parser.add_option("-p", "--password", dest="password", action="store", type="string", help="Password", metavar="PASSWORD")

    (options, args) = parser.parse_args()

    queries=["antibiogram[filter]"]

    if options.organism is None:
        print("Please specify a genus, species or strain name for --organism")
        sys.exit()
    else:
        queries.append(options.organism+"[ORGN]")
    if options.assembly and options.sra:
        parser.error("Error: --assembly and --sra are mutually exclusive. Please provide only one of these options")

    if options.sra:
        queries.append("biosample sra[filter]")
    if options.assembly:
        queries.append("biosample assembly[filter]")

    query=" AND ".join(queries)

    engine = None

    if  options.database is not None and options.user is not None and options.password is not None and options.host is not None:
        engine = create_engine('mysql+pymysql://'+options.user+':'+options.password+'@'+options.host+':3306/'+options.database)

    # Test database connection
    try:
        if engine.connect():
            print("Connected to "+options.database+" as "+options.user)

    except:
        print("Writing to file")


    Session = sessionmaker(bind=engine)
    # create a new session
    session = Session()


    # Get BioSample Accessions for samples that have an antibiogram
    cmd = "esearch -db BioSample -query \""+ query +"\" | efetch -format docsum | xtract -pattern DocumentSummary -element BioSample@accession  Organism -block Attribute -if Attribute@attribute_name -equals strain -def \"N/A\" -element Attribute -block Attribute -if Attribute@attribute_name -equals isolate -def \"N/A\" -element Attribute > biosamples.txt"
    print(cmd)
    os.system(cmd)

    filename=options.out;
    filename=filename.replace(" ","_")

    f = open(filename, 'w')

    header=["sample_accession","organism_name"]
    if options.assembly:
        header.extend(["assembly_accession","assembly_name","assembly_status","organization","ftp_path"])
    if options.sra:
        header.extend(["sra_exp_acc|sra_run_acc|instrument"])
    header.extend(["antibiotic","phenotype","sign","measurement","units","laboratory_typing_method", "laboratory_typing_platform","vendor","laboratory_typing_method_version_or_reagent"])
    f.write("\t".join(header)+"\n")


    phenotypes = {}
    assemblies = {}


    with open('biosamples.txt') as file:
        for line in file:
            metadata = line.rstrip().split("\t")
            biosample=metadata[0]
            species=metadata[1]
            strain=metadata[2]
            try:
                isolate=metadata[3]
            except:
                isolate=""
            species=species.replace("missing","")
            isolate=isolate.replace("missing","")
            if species != "":
                organism=species+" strain "+strain
            if isolate !="":
                organism = species + " isolate " + isolate

            if options.assembly:
                cmd2 = "esearch -db assembly -query "+biosample+" | efetch -format docsum | xtract -pattern DocumentSummary -def \"N/A\" -element AssemblyAccession AssemblyName AssemblyStatus SubmitterOrganization FtpPath_RefSeq > assembly.txt"
                return2=1
                # Keep running until you get a successful return code
                while (return2!=0):
                    print(cmd2)c
                    return2=os.system(cmd2)

                time.sleep(1)
                with open('assembly.txt') as ab_file:
                    for ab_line in ab_file:
                        columns = re.split(r'\t', ab_line.rstrip())

                        assemblies[biosample] = {}
                        assemblies[biosample]['accession'] = columns[0]
                        assemblies[biosample]['name'] = columns[1]
                        assemblies[biosample]['status'] = columns[2]
                        assemblies[biosample]['organization'] = columns[3]
                        assemblies[biosample]['refseq_path'] = columns[4]
            sra_runs = []
            if options.sra:
                cmd2 = "esearch -db sra -query " + biosample + " | efetch -format XML | xtract -pattern EXPERIMENT_PACKAGE -tab \"|\" -element EXPERIMENT@accession RUN@accession INSTRUMENT_MODEL > sra.txt"
                return2 = 1
                # Keep running until you get a successful return code
                while (return2 != 0):
                    print(cmd2)
                    return2 = os.system(cmd2)
                time.sleep(1)

                with open('sra.txt') as sra_file:
                    for sra_line in sra_file:
                        sra_runs.append(sra_line.rstrip())
            # Call no. 3 get the associated antibiogram
            cmd3 = "esearch -db BioSample -query " + biosample + "  | efetch -format xml | xtract -pattern Row -sep \"\\t\" -tab \"\\n\" -def \"N/A\" -element Cell > antibiogram.txt"

            return3=1
            while return3 !=0:
                try:
                    return3=os.system(cmd3)
                except:
                    print(cmd3)
            time.sleep(1)
            with open('antibiogram.txt') as ab_file:
                for ab_line in ab_file:

                    columns = re.split(r'\t', ab_line.rstrip())

                    phenotypes[biosample] = {}
                    phenotypes[biosample]['antibiotic'] = columns[0]
                    phenotypes[biosample]['phenotype'] = columns[1]
                    phenotypes[biosample]['sign'] = columns[2]
                    phenotypes[biosample]['measurement'] = columns[3]
                    phenotypes[biosample]['units'] = columns[4]
                    phenotypes[biosample]['lab_type_method'] = columns[5]
                    for value in columns[6:9]:

                        if value in laboratory_typing_platform:
                            phenotypes[biosample]['lab_typing_platform'] = value

                        if value in vendor:
                            phenotypes[biosample]['vendor'] = value
                        if value in laboratory_typing_method_version_or_reagent:
                            phenotypes[biosample]['lab_typing_method_version_or_reagent'] = value

                        if value in testing_standards:
                            phenotypes[biosample]['testing_standard'] = value


                    if 'measurement_units' not in phenotypes[biosample]:
                        phenotypes[biosample]['measurement_units']=None;
                    if 'testing_standard' not in phenotypes[biosample]:
                        phenotypes[biosample]['testing_standard']=None;
                    if 'lab_typing_method_version_or_reagent' not in phenotypes[biosample]:
                        phenotypes[biosample]['lab_typing_method_version_or_reagent'] = None;
                    if  'vendor' not in phenotypes[biosample]:
                        phenotypes[biosample]['vendor'] = None;
                    if 'lab_typing_platform' not in phenotypes[biosample]:
                        phenotypes[biosample]['lab_typing_platform'] = None;


                    # If a database connection for Pseudomonas Genome Database is in place, insert the new data, otherwise just write it out at the end

                    if engine is not None:
                        biosampleRecord = session.query(GenomeProjectCoreSample).filter(
                            GenomeProjectCoreSample.sample_accession == biosample).first()

                        if biosampleRecord:
                            assemblyRecord = session.query(GenomeProjectSequenceAssembly).filter(
                                GenomeProjectSequenceAssembly.sample_id == biosampleRecord.id).first()
                            if assemblyRecord:
                                strain_record = session.query(Strain).filter(Strain.genome_project_sequence_assembly_id == assemblyRecord.id).first()

                                if strain_record:
                                    strain_ab_record = session.query(StrainAntibioticSusceptibility).filter(
                                        StrainAntibioticSusceptibility.strain_id == strain_record.strain_id,
                                        StrainAntibioticSusceptibility.antibiotic == phenotypes[biosample]['antibiotic'],
                                        StrainAntibioticSusceptibility.phenotype == phenotypes[biosample]['phenotype'],
                                        StrainAntibioticSusceptibility.measurement_sign == phenotypes[biosample]['sign'],
                                        StrainAntibioticSusceptibility.measurement == phenotypes[biosample]['measurement'],
                                        StrainAntibioticSusceptibility.measurement_units == phenotypes[biosample]['units'],
                                        StrainAntibioticSusceptibility.laboratory_typing_method == phenotypes[biosample][
                                            'lab_type_method'],
                                        StrainAntibioticSusceptibility.laboratory_typing_platform == phenotypes[biosample][
                                            'lab_typing_platform'],
                                        StrainAntibioticSusceptibility.vendor == phenotypes[biosample]['vendor'],
                                        StrainAntibioticSusceptibility.laboratory_typing_method_version_or_reagent ==
                                        phenotypes[biosample]['lab_typing_method_version_or_reagent'],
                                        StrainAntibioticSusceptibility.testing_standard == phenotypes[biosample]['testing_standard']).first()



                                    if strain_ab_record is None:


                                        aro_record =session.query(Aro).filter(Aro.term == phenotypes[biosample]['antibiotic']).first()
                                        aro_term = None
                                        if aro_record is not None:

                                            aro_term = aro_record.accession
                                        else:
                                            ab_phenotype=phenotypes[biosample]['antibiotic']
                                            ab_phenotype=ab_phenotype.replace("micin","mycin")

                                            aro_record = session.query(Aro).filter(Aro.term == ab_phenotype).first()
                                            if aro_record:
                                                aro_term = aro_record.accession


                                        strain_ab_record_new = StrainAntibioticSusceptibility(
                                            strain_id=strain_record.strain_id,
                                            antibiotic=phenotypes[biosample]['antibiotic'],
                                            aro_term=aro_term,
                                            phenotype = phenotypes[biosample]['phenotype'],
                                            measurement_sign = phenotypes[biosample]['sign'],
                                            measurement=phenotypes[biosample]['measurement'],
                                            measurement_units =phenotypes[biosample]['units'],
                                            laboratory_typing_method=phenotypes[biosample]['lab_type_method'],
                                            laboratory_typing_platform=phenotypes[biosample]['lab_typing_platform'],
                                            vendor =phenotypes[biosample]['vendor'],
                                            laboratory_typing_method_version_or_reagent=phenotypes[biosample]['lab_typing_method_version_or_reagent'],
                                            testing_standard = phenotypes[biosample]['testing_standard'])
                                        session.add(strain_ab_record_new)
                                        session.commit()

                    f.write(biosample+"\t")
                    f.write(organism + "\t")

                    if options.assembly:

                        if biosample in assemblies:
                            f.write(str(assemblies[biosample]['accession'])+"\t")
                            f.write(str(assemblies[biosample]['name']) + "\t")
                            f.write(str(assemblies[biosample]['status']) + "\t")
                            f.write(str(assemblies[biosample]['organization']) + "\t")
                            f.write(str(assemblies[biosample]['refseq_path']) + "\t")
                        else:
                            f.write("\t")
                            f.write("\t")
                            f.write("\t")
                            f.write("\t")
                            f.write("\t")

                    if options.sra:
                        f.write(" ; ".join(sra_runs)+"\t")

                    f.write(str(phenotypes[biosample]['antibiotic'])+"\t")
                    f.write(str(phenotypes[biosample]['phenotype']) + "\t")
                    f.write(str(phenotypes[biosample]['sign']) + "\t")
                    f.write(str(phenotypes[biosample]['measurement']) + "\t")
                    f.write(str(phenotypes[biosample]['units']) + "\t")
                    f.write(str(phenotypes[biosample]['lab_type_method']).replace("None","") + "\t")
                    f.write(str(phenotypes[biosample]['lab_typing_platform']).replace("None","") + "\t")
                    f.write(str(phenotypes[biosample]['vendor']).replace("None","") + "\t")
                    f.write(str(phenotypes[biosample]['lab_typing_method_version_or_reagent']).replace("None","") + "\n")
                    f.flush()

                    print(biosample, end="\t")
                    print(organism, end="\t")

                    if options.assembly:
                        if biosample in assemblies:
                            print(assemblies[biosample]['accession'], end="\t")
                            print(assemblies[biosample]['name'], end="\t")
                            print(assemblies[biosample]['status'], end="\t")
                            print(assemblies[biosample]['organization'], end="\t")
                            print(assemblies[biosample]['refseq_path'], end="\t")
                        else:
                            print("\t\t\t\t\t")

                    if options.sra:
                        print(" ; ".join(sra_runs))

                    print(phenotypes[biosample]['antibiotic'], end="\t")
                    print(phenotypes[biosample]['phenotype'], end="\t")
                    print(phenotypes[biosample]['sign'], end="\t")
                    print(phenotypes[biosample]['measurement'], end="\t")
                    print(phenotypes[biosample]['units'], end="\t")
                    print(str(phenotypes[biosample]['lab_type_method']).replace("None",""), end="\t")
                    print(str(phenotypes[biosample]['lab_typing_platform']).replace("None",""), end="\t")
                    print(str(phenotypes[biosample]['vendor']).replace("None",""), end="\t")
                    print(str(phenotypes[biosample]['lab_typing_method_version_or_reagent']).replace("None",""), end="\n")

    f.close()


laboratory_typing_platform = ['Microscan', 'Phoenix', 'Sensititre', 'Vitek']
vendor = ['Becton Dickinson', 'Biomérieux', 'Siemens', 'Trek', 'Biom?rieux', 'Biomerieux']
laboratory_typing_method_version_or_reagent = ['96-Well Plate', 'E-Test', 'GM-NEG']
testing_standards = ['BSAC', 'CLSI', 'DIN', 'EUCAST', 'NARMS', 'NCCLS', 'SFM', 'SIR', 'WRG']

if __name__ == '__main__':
    main()
