## CurrentBookingsExport

this example shows how to write a python script to retrieve bookings active on a particular date and export them to excel
it will also lookup the release and environment names instead of just the ids 

## dockerhealthcheck

This shows how you can write a python script that find environments with a status of Active - Auto and dinds the docker services 
that are run for that environment
If they are all up it sends an up status to the healthcheck dashboard for that environment
If any of them are down it sends a down to the health check dashboard