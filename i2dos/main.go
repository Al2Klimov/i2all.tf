package main

import (
	"bufio"
	"bytes"
	"crypto/tls"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"math/rand"
	"net"
	"net/http"
	"net/url"
	"strings"
	"sync"
)

var client = &http.Client{
	Transport: &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
		},
	},
}

var (
	concurrency = flag.Uint("c", 0, "NUMBER")
	host        = flag.String("H", "", "HOSTNAME")
	user        = flag.String("u", "", "USERNAME")
	pass        = flag.String("p", "", "PASSWORD")
)

var (
	services [][2]string
	outMtx   sync.Mutex
)

func main() {
	flag.Parse()

	if *concurrency == 0 {
		panic("-c missing")
	}

	if *host == "" {
		panic("-H missing")
	}

	if *user == "" {
		panic("-u missing")
	}

	if *pass == "" {
		panic("-p missing")
	}

	var resp struct {
		Results []struct {
			Name string `json:"name"`
		} `json:"results"`
	}

	if err := i2j("GET", "/v1/objects/services", map[string][]string{"attrs": {"name"}}, &resp); err != nil {
		panic(err)
	}

	services = make([][2]string, 0, len(resp.Results))
	for _, service := range resp.Results {
		hs := strings.SplitN(service.Name, "!", 2)
		services = append(services, [2]string{hs[0], hs[1]})
	}

	for i := *concurrency; i > 0; i-- {
		go dos()
	}

	select {}
}

func dos() {
	for {
		hs := services[rand.Intn(len(services))]

		err := i2j(
			"GET",
			"/v1/objects/services",
			map[string]interface{}{
				"filter":      "host.name==hn && service.name==sn",
				"filter_vars": map[string]string{"hn": hs[0], "sn": hs[1]},
			},
			&struct{}{},
		)

		func() {
			outMtx.Lock()
			defer outMtx.Unlock()

			if err == nil {
				fmt.Print(".")
			} else {
				fmt.Println()
				fmt.Print(err.Error())
			}
		}()
	}
}

func i2j(method string, path string, body interface{}, output interface{}) error {
	buf := &bytes.Buffer{}
	if err := json.NewEncoder(buf).Encode(body); err != nil {
		return err
	}

	response, err := client.Do(&http.Request{
		Method: method,
		URL: &url.URL{
			Scheme: "https",
			User:   url.UserPassword(*user, *pass),
			Host:   net.JoinHostPort(*host, "5665"),
			Path:   path,
		},
		Header:        http.Header{"Accept": []string{"application/json"}},
		Body:          io.NopCloser(buf),
		ContentLength: int64(buf.Len()),
	})
	if err != nil {
		return err
	}

	defer func() { _ = response.Body.Close() }()

	return json.NewDecoder(bufio.NewReader(response.Body)).Decode(output)
}
