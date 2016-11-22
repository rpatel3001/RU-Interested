package com.rpatel3001.ru_interested;

import android.content.Context;
import android.graphics.Point;
import android.util.AttributeSet;
import android.view.WindowManager;
import android.widget.RelativeLayout;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

public class ClassDisplayView extends RelativeLayout {
    TextView name, room, time, department, coursenum;

    public ClassDisplayView(Context context) {
        super(context);
        init();
    }

    public ClassDisplayView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public ClassDisplayView(Context context, AttributeSet attrs, int defStyle) {
        super(context, attrs, defStyle);
        init();
    }

    public void init() {
        inflate(getContext(), R.layout.view_class_display, this);

        name = (TextView)findViewById(R.id.name);
        room = (TextView)findViewById(R.id.room);
        time = (TextView)findViewById(R.id.time);
        department = (TextView)findViewById(R.id.department);
        coursenum = (TextView)findViewById(R.id.coursenum);
    }

    public void setValues(JSONObject json) throws JSONException {
        name.setText(json.getString("title"));
        room.setText(json.getString("building") + "-" + json.getString("room"));
        time.setText(json.getString("time"));
        department.setText(json.getString("department"));
        coursenum.setText(json.getString("deptcode") + ":" + json.getString("coursecode"));
    }
}
