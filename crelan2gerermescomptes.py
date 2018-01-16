import sys
import csv  # For CSV file reading, parsing and writing
import re   # For regular expression

if __name__ == '__main__':
    verbose = 0

    # This script needs one argument: the input file to parse
    if len(sys.argv) < 2:
        print("Please, specify the filename you want to parse")
        print("Example: python %s crelan-export.csv" % sys.argv[0])
        sys.exit()

    print("Opening file %s..." % sys.argv[1])
    csv.register_dialect('myDialect', delimiter=';', quoting=csv.QUOTE_MINIMAL)

    with open(sys.argv[1], 'rb') as fin:
        with open('out.csv', 'wb') as fout:
            reader = csv.reader(fin, dialect='myDialect')
            writer = csv.writer(fout, dialect='myDialect')

            # Create the header of the output file
            header = ['Date de valeur', 'Date operation', 'Montant', 'Contrepartie', "Type d'operation",
                       'Communication']
            writer.writerow(header)

            # Display it on the screen
            print("Date de valeur;Date de l'operation;Montant;Contrepartie;Type d'operation;Communication")

            # Don't parse line #1, this is the header
            line = 1

            for read_row in reader:
                if line != 1:
                    # Extract useful fields
                    date_de_valeur = read_row[0]
                    montant = read_row[1]
                    contrepartie = read_row[3]
                    type_operation = read_row[5]
                    communication = read_row[6]

                    # Parse the "Communication" field for type
                    # - "Paiement Bancontact",
                    # - "Retrait Bancontact",
                    # - "Paiement Maestro",
                    # - "Retrait maestro"
                    #
                    #  ... to extract the transaction date in the "Communication" field

                    if type_operation == "Paiement Bancontact" or type_operation == "Retrait Bancontact" \
                            or type_operation == "Paiement Maestro" or type_operation == "Retrait maestro":
                        # Parse the "Communication" field, looking for the operation date
                        m = re.search(r'\d{2}-\d{2}-\d{4}', communication)
                        if m is not None:
                            date_operation = m.group()
                        else:
                            date_operation = "01-01-2050"   # Meaning not found"
                    else:
                        date_operation = date_de_valeur

                    # Since May 2017, there is a parsing error for "Paiement Maestro":
                    # The "contrepartie" field contains the city name
                    # Let's try to extract the "contrepartie" from the "Communication" field

                    if type_operation == "Paiement Maestro":
                        m = re.search(r'\d{16} ', communication)
                        if m is None:
                            # This is the new structure (>= May 2017)
                            # Extract the "contrepartie" from the "Communication" field
                            contrepartie = communication[:24]

                    row_to_write = []
                    row_to_write.append(date_de_valeur)
                    row_to_write.append(date_operation)
                    row_to_write.append(montant)
                    row_to_write.append(contrepartie)
                    row_to_write.append(type_operation)
                    row_to_write.append(communication)
                    writer.writerow(row_to_write)

                    print("%s;%s;%s;%s;%s;%s" % (date_de_valeur, date_operation, montant, contrepartie, type_operation, communication))

                # To parse next line
                line += 1
        fout.close()
    fin.close()