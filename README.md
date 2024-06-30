# Cloudflare Address List Update Docker

This Dockerized solution periodically updates two address lists on a MikroTik router with Cloudflare's IPv4 and IPv6 addresses. It also adds the IPv6 address of a specified local interface to another address list (`proxyv6`) on the router.

## Requirements

- Docker
- MikroTik router with API access enabled
- Cloudflare API for IPv6 addresses
- Environment variables for configuration:
  - `ROUTER_IP`: IP address of the MikroTik router.
  - `PASSWORD`: Password for MikroTik API access.
  - `USERNAME`: MikroTik router username.
  - `IFNAME`: Name of the local interface whose IPv6 address should be added to `proxyv6`. leave empty disables updating the proxyv6 list

## Usage

1. **Build the Docker Image:**

   ```bash
   docker build -t update-cloudflare-mikrotik .
   ```

2. **Run the Docker:**

    ```bash
    docker run -d --name update-cloudflare-mikrotik \
    -e ROUTER_IP='192.168.88.1' \
    -e PASSWORD='YOUR_PASSWORD_HERE' \
    -e USERNAME='your-username' \
    -e IFNAME='eth0' \
    update-cloudflare-mikrotik
    ```

    Certainly! Here's the complete content of the `README.md` file, including the Docker Compose section, in a single raw format:

```markdown
# Cloudflare Address List Update Docker

This Dockerized solution periodically updates two address lists on a MikroTik router with Cloudflare's IPv4 and IPv6 addresses. It also adds the IPv6 address of a specified local interface to another address list (`proxyv6`) on the router.

## Requirements

- Docker
- Docker Compose
- MikroTik router with API access enabled
- Environment variables for configuration:
  - `ROUTER_IP`: IP address of the MikroTik router.
  - `PASSWORD`: Password for MikroTik API access.
  - `USERNAME`: MikroTik router username.
  - `IFNAME`: Name of the local interface whose IPv6 address should be added to `proxyv6`. leave empty disables updating the proxyv6 list

## Usage

### Using Docker Compose

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/potoonite/cloudflare-mikrotik-docker.git
   cd cloudflare-mikrotik-docker
   ```

2. **Set Environment Variables:**

   Create a `.env` file in the root directory with the following content:

   ```plaintext
   ROUTER_IP=192.168.88.1
   PASSWORD=YOUR_API_TOKEN
   USERNAME=your-username
   IFNAME=eth0
   ```

   Replace `ROUTER_IP`, `PASSWORD`, `USERNAME`, and `IFNAME` with your actual values.

3. **Run Docker Compose:**

   ```bash
   docker-compose up -d
   ```

4. **Verify Container Logs:**

   ```bash
   docker-compose logs -f
   ```

   Check the logs to ensure that Cloudflare address updates and `proxyv6` list updates are occurring correctly.

## Functionality

- **Cloudflare Address Update:** Fetches Cloudflare's IPv4 and IPv6 addresses using their API and updates two address lists `cloudflarev4` and `cloudflarev6` on the MikroTik router.
  
- **Local Interface Address Update:** Retrieves the IPv6 address of the specified local interface (`IFNAME`) and adds it to the `proxyv6` address list on the MikroTik router for firewall rule references.

## Troubleshooting

- Ensure that the MikroTik API credentials (`ROUTER_IP`, `PASSWORD`, `USERNAME`) are correctly configured and have sufficient permissions.
  
- Verify network connectivity from the Docker container to the MikroTik router and Cloudflare's API endpoint.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.