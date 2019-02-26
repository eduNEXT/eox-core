import React from 'react';
import ReactDOM from 'react-dom';
import { Tabs } from '@edx/paragon';
import { CourseTeamManagement } from './CourseTeamManagement'
import { CourseSettings } from './CourseSettings'
import { CourseRerun } from './CourseRerun'
import '../css/edx-bootstrap'

function CourseManagement(props) {
  return (
    <Tabs labels={["Course team management", "Course settings", "Course rerun"]}>
      <div>
        <CourseTeamManagement
          orgList={props.teamManagement.list_org}
          requestTimeOut={props.teamManagement.request_timeout_value}
        />
      </div>
      <div>
        <CourseSettings
          courseKey={props.courseSettings.course_key}
          detailsFields={props.courseSettings.details_fields}
          requestTimeOut={props.courseSettings.request_timeout_value}
        />
      </div>
      <div>
        <CourseRerun
          requestTimeOut={props.courseRerun.request_timeout_value}
        />
      </div>
    </Tabs>
  );
}

export class RenderReactComponent {

  constructor(properties={}) {
    Object.assign(this, {
      properties
    });
    this.renderReact();
  }

  renderReact() {
    ReactDOM.render(
      React.createElement(CourseManagement, this.properties, null),
      document.getElementById('root')
    );
  }
}

