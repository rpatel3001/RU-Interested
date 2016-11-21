package com.rpatel3001.ru_interested;

import android.content.Intent;
import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class DisplayMessageActivity extends AppCompatActivity {

    private TextView textView;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_display_message);
        findViewById(R.id.textPanel).setVisibility(View.INVISIBLE);

        Intent intent = getIntent();
        String message = intent.getStringExtra(MainActivity.EXTRA_MESSAGE);
        textView = new TextView(this);
        textView.setTextSize(40);
        textView.setText(message);

        ViewGroup layout = (ViewGroup) findViewById(R.id.activity_display_message);
        layout.addView(textView);
        new DownloadWebpageTask().execute("http://ru-interested.herokuapp.com/api/classes/BUS/M/0800/2200");
    }

    private String downloadUrl(String myurl) throws IOException {
        URL url = new URL(myurl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        Scanner s = new Scanner(conn.getInputStream()).useDelimiter("\\A");
        return s.hasNext() ? s.next() : "";
    }

    private class DownloadWebpageTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... urls) {
            try {
                return downloadUrl(urls[0]);
            } catch (IOException e) {
                return e.getStackTrace().toString();
            }
        }
        // onPostExecute displays the results of the AsyncTask.
        @Override
        protected void onPostExecute(String result) {
            try {
                JSONArray rooms = new JSONArray(result);
                textView.setText(Integer.toString(rooms.length()));
            } catch (JSONException e) {
                e.printStackTrace();
            }
            findViewById(R.id.loadingPanel).setVisibility(View.GONE);
            findViewById(R.id.textPanel).setVisibility(View.VISIBLE);
        }
    }
}
