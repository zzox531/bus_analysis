import argparse
from bus_analysis import scraper, analyze

def main():
    parser = argparse.ArgumentParser(description="Bus Analysis Tool")
    
    # Adding arguments for scraper functions
    parser.add_argument(
        '--get_busstop_info', 
        metavar='FILENAME', 
        type=str,
        help='Get bus stop information from a file'
    )

    parser.add_argument(
        '--get_busstop_loc_info', 
        metavar=('BUSSTOPFILE', 'OUTPUTFILE'), 
        nargs=2,
        help='Get bus stop location information and save to file'
    )

    parser.add_argument(
        '--get_bus_info', 
        metavar=('FILENAME', 'LINES'),
        nargs=2,
        help='Get bus information for a specific time window'
    )

    parser.add_argument(
        '--get_bus_schedule', 
        metavar=('BUSSTOPFILE', 'SCHEDULEFILE'), 
        nargs=2,
        help='Get and save the bus schedule based on bus stop information'
    )

    # Adding arguments for analyze functions
    parser.add_argument(
        '--get_speeding_info', 
        metavar=(
            'DATAFILE', 
            'LINES_CSV', 
            'LOC_CSV', 
            'OUTPUT_HTML'
        ),
        nargs=4,
        help='Analyze and output speeding information from data files')
    parser.add_argument(
        '--get_lateness_info', 
        metavar=(
            'DATAFILE', 
            'SCHEDULEFILE', 
            'BUSSTOPLOCFILE', 
            'LATE_LINES_CSV', 
            'LATE_BSTOPS_CSV', 
            'OUTPUT_HTML'
        ), 
        nargs=6,
        help='Analyze and output buses punctuality information from data files'
    )

    # Parse the arguments
    args = parser.parse_args()

    # Executing scraper functions based on the arguments
    if args.get_busstop_info:
        scraper.get_busstop_info(args.get_busstop_info)
    
    if args.get_busstop_loc_info:
        busstop_file, output_file = args.get_busstop_loc_info
        scraper.get_busstop_loc_info(busstop_file, output_file)
    
    if args.get_bus_info:
        file_name, lines = args.get_bus_info
        scraper.get_bus_info(file_name, int(lines))
    
    if args.get_bus_schedule:
        busstop_file, schedule_file = args.get_bus_schedule
        scraper.get_bus_schedule(busstop_file, schedule_file)

    # Executing analyze functions based on the arguments
    if args.get_speeding_info:
        data_file, lines_csv, loc_csv, output_html = args.get_speeding_info
        analyze.get_speeding_info(data_file, lines_csv, loc_csv, output_html)
    
    if args.get_lateness_info:
        data_file, schedule_file, busstoploc_file, late_lines_csv, late_bstops_csv, output_html = args.get_lateness_info
        analyze.get_lateness_info(
            data_file, 
            schedule_file, 
            busstoploc_file, 
            late_lines_csv, 
            late_bstops_csv, 
            output_html
        )

if __name__ == "__main__":
    main()